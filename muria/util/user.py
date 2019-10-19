"""User Authentication Factory."""

from muria.db.model import User
from muria.db.schema import _Credentials
from pony.orm import db_session
from muria.util.tokenizer import (
    TokenBasic,
    TokenJWT,
    InvalidTokenError
)
from falcon import (
    HTTPUnprocessableEntity,
    HTTPUnauthorized
)


class UserAuthentication(object):
    """Authenticate user based on username and password."""

    def __init__(self, config):

        self.login_schema = _Credentials()
        token_basic = TokenBasic(config)
        token_jwt = TokenJWT(config)
        self._tokenizers = {'basic': token_basic, 'jwt': token_jwt}
        self.tokenizer = self._tokenizers['basic']

    @db_session
    def authenticate_user(self, username, password, token_type='basic'):
        """Authenticate user with their username and password."""

        self.tokenizer = self._tokenizers.get(token_type)
        credentials = {"username": username, "password": password}
        errors = self.login_schema.validate(credentials)
        if errors:
            raise HTTPUnprocessableEntity(
                code=88810,  # unprocessable creds either blank or invalid
                title="Authentication Failure",
                description=str(errors)
            )
        user = User.get(username=credentials["username"])
        if user and user.check_password(credentials["password"]):
            payload = self.tokenizer.create_payload(user.username)
            return self.tokenizer.create_token(payload, user.username)
        else:
            raise HTTPUnauthorized(
                code=88811,  # credentials received but invalid
                title="Authentication Failure",
                description="Invalid credentials"
            )

    @db_session
    def check_token(self, token):
        access_token = None
        failure = None
        for i in self._tokenizers:
            try:
                access_token = self._tokenizers[i].verify_token(token)
                break
            except InvalidTokenError as error:
                failure = error
                continue

        if access_token:
            return access_token
        else:
            raise HTTPUnauthorized(
                code=failure.code,
                title="Token Verification",
                description=failure.status
            )

    @db_session
    def refresh_token(self, access_token, refresh_token):
        refreshed_tokens = None
        failure = None
        for i in self._tokenizers:
            try:
                refreshed_tokens = self._tokenizers[i].refresh_token(
                    access_token, refresh_token
                )
                break
            except InvalidTokenError as error:
                failure = error
                continue

        if refreshed_tokens:
            return refreshed_tokens
        else:
            raise HTTPUnauthorized(
                code=failure.code,
                title="Token Verification",
                description=failure.status
            )
