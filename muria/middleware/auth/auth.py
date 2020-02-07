"""Authentication Resource."""

from .token import Jwt
from .middleware import AuthMiddleware
from pony.orm import db_session
from muria.db import User, JwtToken
from muria.db.schema import Credentials
from datetime import datetime
from os import environ, urandom, path
import base64
from falcon import (
    HTTP_OK,
    HTTPBadRequest,
    HTTPUnprocessableEntity,
    HTTPUnauthorized,
    HTTP_RESET_CONTENT
)


def default_secret_key(size=32):
    try:
        key = environ["AUTH_TOKEN_KEY"]
    except KeyError:
        key = environ["AUTH_TOKEN_KEY"] = urandom(int(size)).hex()
    finally:
        return key


class Auth(object):

    def __init__(self, **auth_config):
        default_auth_config = {
            "route_basepath": "v1",
            "route_path": "auth",
            "secret_key": default_secret_key(32),
            "algorithm": "HS256",
            "jwt_header_prefix": "jwt",
            "jwt_refresh_header_prefix": "ref",
            "jwt_token_exp": 1800,
            "jwt_refresh_exp": 604800,
            "leeway": 0,
            "audience": "https://localhost",
            "issuer": "https://localhost",
            "exempt_routes": [],
            "exempt_methods": ['OPTIONS'],
            "cache": None
        }
        for auth_setting, setting_value in default_auth_config.items():
            auth_config.setdefault(auth_setting, setting_value)

        unknown_settings = list(
            set(auth_config.keys()) - set(default_auth_config.keys())
        )
        if unknown_settings:
            raise ValueError(
                "Unknown Auth settings: {0}".format(unknown_settings)
            )

        if not auth_config["route_path"]:
            auth_config["route_path"] = "auth"

        self.path = path.join("/", auth_config["route_basepath"],
                              auth_config["route_path"])

        self.exempt_routes = auth_config["exempt_routes"] or []
        self.exempt_methods = auth_config["exempt_methods"] or ['OPTIONS']

        self.cache = auth_config["cache"] or None

        self._auth_config = auth_config

        self.tokenizer = Jwt(
            secret_key=auth_config.get("secret_key"),
            algorithm=auth_config.get("algorithm"),
            token_header_prefix=auth_config.get("jwt_header_prefix"),
            leeway=auth_config.get("leeway"),
            expiration_delta=auth_config.get("jwt_token_exp"),
            audience=auth_config.get("audience"),
            issuer=auth_config.get("issuer")
        )

        self.refresher = Jwt(
            secret_key=auth_config.get("secret_key"),
            algorithm=auth_config.get("algorithm"),
            token_header_prefix=auth_config.get("jwt_refresh_header_prefix"),
            leeway=auth_config.get("leeway"),
            expiration_delta=auth_config.get("jwt_refresh_exp"),
            audience=auth_config.get("audience"),
            issuer=auth_config.get("issuer")
        )

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

    @property
    def middleware(self):
        return AuthMiddleware(self)

    @db_session
    def acquire(self, req, resp):
        # authenticate user credentials via json, form_urlencoded or
        # auth basic header digest

        if req.media:
            username = req.media.get("username", "")
            password = req.media.get("password", "")
        # auth basic header
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
        # generate token along with its refresh token
        now = datetime.utcnow().timestamp()
        data = {"id": user.get_user_id(), "rand": urandom(3).hex()}
        token = self.tokenizer.create_token(data)
        signature = {"signature": self._get_token_key(token)}
        refresh_token = self.refresher.create_token(signature)
        jwt = JwtToken(
            token_type=self._auth_config.get("jwt_header_prefix"),
            access_token=token,
            expires_in=int(self._auth_config.get("jwt_token_exp")),
            refresh_expires_in=int(self._auth_config.get("jwt_refresh_exp")),
            issued_at=now,
            refresh_token=refresh_token,
            user=user,
            access_key=self._get_token_key(token),
            refresh_key=self._get_token_key(refresh_token)
        )
        resp.media = jwt.unload()
        resp.status = HTTP_OK

    def verify(self, req, resp):
        # unauthorized token if already revoked
        # otherwise send it back if valid

        token = self.tokenizer.parse_token_header(req)
        if self.is_token_revoked(token):
            raise HTTPUnauthorized()

        payload = self.tokenizer.unload(token)
        if payload.get("id"):
            resp.media = {"access_token": token}
            resp.status = HTTP_OK
        else:
            raise HTTPBadRequest()

    @db_session
    def refresh(self, req, resp):

        # TODO:
        # 1. refresh revoke checking
        # 2. implement rate limiting to prevent DDoS
        old_refresh_token = self.refresher.parse_token_header(req)
        old_refresh_payload = self.refresher.unload(old_refresh_token)

        if req.media and req.media.get("access_token") and old_refresh_payload:

            old_token = req.media.get("access_token")
            # jwt revoke checking
            if self.is_token_revoked(old_token):
                # unauthorized token pair for hard revoke
                # otherwise allow them to refresh
                # if you want to implement soft revoke
                raise HTTPUnauthorized()
            old_token_payload = self.tokenizer.unload(
                old_token, options={'verify_exp': False})

            try:
                if old_refresh_payload["signature"] == old_token.split(".")[2]:
                    now = datetime.utcnow().timestamp()
                    old_token_payload.update({"rand": urandom(3).hex()})
                    user = User.get(id=old_token_payload["id"])
                    token = self.tokenizer.create_token(old_token_payload)
                    signature = {"signature": self._get_token_key(token)}
                    refresh_token = self.refresher.create_token(signature)
                    jwt = JwtToken(
                        token_type=self._auth_config.get("jwt_header_prefix"),
                        access_token=token,
                        expires_in=self._auth_config.get("jwt_token_exp"),
                        refresh_expires_in=self._auth_config.get(
                            "jwt_refresh_exp"),
                        issued_at=now,
                        refresh_token=refresh_token,
                        user=user,
                        access_key=self._get_token_key(token),
                        refresh_key=self._get_token_key(refresh_token)
                    )
                    self._revoke_token(old_token)
                    resp.media = jwt.unload()
                    resp.status = HTTP_OK
            except Exception:
                raise HTTPBadRequest()
        else:
            raise HTTPBadRequest()

    def revoke(self, req, resp):
        token = self.tokenizer.parse_token_header(req)
        if self.is_token_revoked(token):
            raise HTTPUnauthorized()

        payload = self.tokenizer.unload(token)
        if payload.get("id") and self._revoke_token(token):
            resp.status = HTTP_RESET_CONTENT

    @db_session
    def _revoke_token(self, token):
        # TODO:
        # 1. revoke only token for soft revoke
        # 2. revoke both for hard revoke
        jwt = JwtToken.get(access_key=self._get_token_key(token))
        if jwt and jwt.revoked is False:
            jwt.revoked = True
            expiry = jwt.get_expires_at() - datetime.utcnow().timestamp()
            self._cache_revoked_token(token, expiry)
            return True
        else:
            return False

    def _cache_revoked_token(self, token, expiry=1800):
        if self.cache:
            try:
                # expire argument must be int
                self.cache.set(self._get_token_key(token), token, int(expiry))
            except Exception as err:
                # TODO:
                # use logger here
                pass

    @db_session
    def is_token_revoked(self, token):
        if self.cache:
            try:
                key = self._get_token_key(token)
                return self.cache.get(key) == token
            except Exception as err:
                # TODO:
                # use logger here
                pass
        return JwtToken.exists(access_key=self._get_token_key(token),
                               revoked=True)

    @staticmethod
    def _get_token_key(token):
        parts = token.split(".")

        if len(parts) != 3:
            return ''
        return parts[2]
