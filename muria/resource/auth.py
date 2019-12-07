"""Authentication Resource."""

from muria.common.resource import Resource
from muria.init import user_authentication, DEBUG
from pony.orm import db_session
from muria.util.tokenizer import extract_auth_header
from falcon import (
    HTTP_OK,
    HTTPBadRequest
)


class Authentication(Resource):
    """Authentication Resource.

    Authenticate user with their credentials and issues token for them.
    """

    @db_session
    def on_get(self, req, resp):
        """Ping like end-point.
        ---
        tags:
        - auth
        summary: Ping auth end-point
        operationId: pingAuth
        parameters:
            - in: header
              name: origin
              type: string
              required: true
              description: CORS request origin
        responses:
            200:
                description: Ping response
        """

        resp.status = HTTP_OK
        resp.set_header("WWW-Authenticate", "Bearer")
        if DEBUG:
            resp.media = {"Ping": "Pong"}

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
                schema: BasicToken
            400:
                description: Bad request dou to invalid credentials
        """
        if req.media:
                token = user_authentication.authenticate_user(
                    username=req.media.get("username", ""),
                    password=req.media.get("password", "")
                )
        elif req.headers.get("AUTHORIZATION"):
            username, password = extract_auth_header(
                req.headers.get("AUTHORIZATION", "")
            )
            token = user_authentication.authenticate_user(
                username=username,
                password=password
            )
        else:
            raise HTTPBadRequest()

        resp.status = HTTP_OK
        resp.media = token


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
                schema: BasicToken
            400:
                description: Bad request dou to invalid access token
        """

        if req.media:
            token = user_authentication.check_token(
                req.media.get("access_token", "")
            )
            content = {"access_token": token}
            resp.status = HTTP_OK
            resp.media = content
        else:
            raise HTTPBadRequest()


class Refresh(Resource):
    """Refresh Token Resource.

    Replace an old token with new one.
    """

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
                schema: BasicToken
            400:
                description: Bad request dou to invalid token pair
        """
        if req.media:
            access_token = req.media.get("access_token", "")
            refresh_token = req.media.get("refresh_token", "")
            resp.media = user_authentication.refresh_token(
                access_token, refresh_token
            )
            resp.status = HTTP_OK
        else:
            raise HTTPBadRequest()
