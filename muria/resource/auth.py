"""Authentication Resource."""

from muria import config
from muria.common.resource import Resource
from pony.orm import db_session
from muria.db import User, JwtToken as JwtTokenEntity
from muria.db.schema import Credentials
from muria.middleware.auth import JwtToken
from datetime import datetime
from os import urandom
import base64
from falcon import (
    HTTP_OK,
    HTTPBadRequest,
    HTTPUnprocessableEntity,
    HTTPUnauthorized
)


jwt_tokenizer = JwtToken(
    unloader=lambda payload: payload.get("data"),
    secret_key=config.get("jwt_secret_key"),
    algorithm=config.get("jwt_algorithm"),
    token_header_prefix=config.get("jwt_header_prefix"),
    leeway=config.getint("jwt_leeway"),
    expiration_delta=config.getint("jwt_token_exp"),
    audience=config.get("jwt_audience"),
    issuer=config.get("jwt_issuer")
)


jwt_refresh_tokenizer = JwtToken(
    unloader=lambda payload: payload.get("data"),
    secret_key=config.get("jwt_secret_key"),
    algorithm=config.get("jwt_algorithm"),
    token_header_prefix=config.get("jwt_refresh_header_prefix"),
    leeway=config.getint("jwt_leeway"),
    expiration_delta=config.getint("jwt_refresh_exp"),
    audience=config.get("jwt_audience"),
    issuer=config.get("jwt_issuer")
)


class Authentication(Resource):
    """Authentication Resource.

    Authenticate user with their credentials and issues token for them.
    """

    def _get_auth_header(self, auth_header, prefix):
        parts = auth_header.split()
        if parts[0].lower() != prefix:
            raise HTTPUnauthorized(
                description='Invalid Authentication Header: '
                'Must start with `basic`')
        elif len(parts) == 1:
            raise HTTPUnauthorized(
                description='Invalid Authorization Header: Token Missing')
        elif len(parts) > 2:
            raise HTTPUnauthorized(
                description='Invalid Authorization Header: '
                'Contains extra content')
        decoded = base64.urlsafe_b64decode(parts[1]).decode('utf8')
        # return tuple of username and password
        return decoded.split(':')

    @db_session
    def on_post(self, req, resp):
        """User authentication end-point
        ---
        tags:
        - auth
        summary: Authenticate user with their credentials
        operationId: authUser
        consumes:
        - application/json
        - application/x-www-form-urlencoded
        produces:
        - application/json
        parameters:
            - in: header
              name: origin
              type: string
              required: true
              description: CORS request origin
            - in: body
              name: credentials
              required: true
              description: User credentials
              schema:
                type: object
                required:
                - username
                - password
                properties:
                  username:
                    type: string
                  password:
                    type: string
                    format: password
        responses:
            200:
                description: Acquire basic token
                schema: BearerToken
            400:
                description: Bad request due to invalid credentials
        """
        if req.media:
            username = req.media.get("username", "")
            password = req.media.get("password", "")

        elif req.get_header("AUTHORIZATION"):
            username, password = self._get_auth_header(
                req.get_header('AUTHORIZATION'), prefix='basic')
        else:
            raise HTTPBadRequest()

        errors = Credentials().validate(
            {"username": username, "password": password}
        )
        if errors:
            raise HTTPUnprocessableEntity(
                code=88810,  # unprocessable creds either blank or invalid
                title="Authentication Failure",
                description=str(errors)
            )

        user = User.authenticate(username=username, password=password)
        if not user:
            raise HTTPUnauthorized(
                code=88811,  # credentials received but invalid
                title="Authentication Failure",
                description="Invalid credentials"
            )

        # TODO: use rbac caching system for fast lookup of payload
        now = datetime.utcnow().timestamp()
        data = {"id": user.get_user_id(), "rand": urandom(3).hex()}
        token = jwt_tokenizer.create_token(data)
        signature = {"token_sig": token.split(".")[2]}
        refresh_token = jwt_refresh_tokenizer.create_token(signature)
        jwt = JwtTokenEntity(
            token_type=self.config.get("jwt_header_prefix"),
            access_token=token,
            expires_in=self.config.getint("jwt_token_exp"),
            issued_at=now,
            refresh_token=refresh_token,
            user=user
        )
        resp.media = jwt.unload()
        resp.status = HTTP_OK


class Verification(Resource):
    """Verification Resource.

    Verifies submitted access_token or refresh_token
    """

    def on_post(self, req, resp, **params):
        # TODO:
        # implement some cache validations on the user
        """Token verification
        ---
        tags:
        - auth
        summary: Verifies submitted token
        operationId: verifyToken
        consumes:
        - application/json
        produces:
        - application/json
        parameters:
            - in: header
              name: origin
              type: string
              required: true
              description: CORS request origin
            - in: body
              name: access_token
              required: true
              description: access token
              schema:
                type: object
                required:
                - access_token
                properties:
                  access_token:
                    type: string
        responses:
            200:
                description: Verified token
                schema: BearerToken
            400:
                description: Bad request due to invalid access token
        """

        if hasattr(req.context, 'user'):
            header = req.get_header('AUTHORIZATION')
            resp.status = HTTP_OK
            resp.media = {"access_token": header.split()[1]}
        else:
            raise HTTPBadRequest()


class Refresh(Resource):
    """Refresh Token Resource.

    Replace an old token with new one.
    """
    auth = {
        'auth_disabled': True
    }

    def on_post(self, req, resp, **params):
        """Token refresh
        ---
        tags:
        - auth
        summary: Refresh and old token
        operationId: refreshToken
        consumes:
        - application/json
        produces:
        - application/json
        parameters:
            - in: header
              name: origin
              type: string
              required: true
              description: CORS request origin
            - in: body
              name: token
              required: true
              description: token pair
              schema:
                type: object
                required:
                - access_token
                - refresh_token
                properties:
                  access_token:
                    type: string
                  refresh_token:
                    type: string
        responses:
            200:
                description: Refreshed token
                schema: BearerToken
            400:
                description: Bad request due to invalid token pair
        """
        if req.media and req.media.get("access_token") \
                and req.media.get("refresh_token"):
            # TODO:
            # 1. use caching system for invalidate previous jwt token
            # 2. implement rate limiting to prevent DDoS

            # extract wannabe expired token
            old_token = req.media.get("access_token")
            old_payload = jwt_tokenizer.unload(
                old_token, options={'verify_exp': False})
            # verify supplied refresh token
            old_refresh_token = req.media.get("refresh_token")
            old_refresh_payload = jwt_refresh_tokenizer.unload(
                old_refresh_token)

            if old_payload and old_refresh_payload:
                now = datetime.utcnow().timestamp()
                token = jwt_tokenizer.create_token(old_payload)
                signature = {"token_sig": token.split(".")[2]}
                refresh = jwt_refresh_tokenizer.create_token(
                    signature)
                resp.media = {
                    "token_type": self.config.get("jwt_header_prefix"),
                    "access_token": token,
                    "expires_in": self.config.getint("jwt_token_exp"),
                    "issued_at": now,
                    "refresh_token": refresh
                }
                resp.status = HTTP_OK
        else:
            raise HTTPBadRequest()
