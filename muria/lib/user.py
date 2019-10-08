"""User Authentication Factory."""

from muria.db.model import User
from muria.db.schema import _Credentials
from pony.orm import db_session
from muria.lib.tokenizer import (
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

    def __init__(self, config, login_schema=_Credentials):

        self._login_schema = login_schema()
        token_basic = TokenBasic(config)
        token_jwt = TokenJWT(config)
        self._tokenizers = {'basic': token_basic, 'jwt': token_jwt}
        self.tokenizer = self._tokenizers['basic']

    @db_session
    def authenticate_user(self, username, password, token_type='basic'):
        """Authenticate user with their username and password."""

        self.tokenizer = self._tokenizers.get(token_type)
        payload = {"username": username, "password": password}
        data, errors = self._login_schema.load(payload)
        if errors:
            raise HTTPUnprocessableEntity(
                code=88810,  # unprocessable creds either blank or invalid
                title="Authentication Failure",
                description=str(errors)
            )
        user = User.get(username=data["username"])
        if user and user.check_password(data["password"]):
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
        error_code = None
        for i in self._tokenizers:
            try:
                self._tokenizers[i].is_token(token)
            except InvalidTokenError as failure:
                error_code = failure.code
                continue
            try:
                return self._tokenizers[i].verify_token(token)
            except InvalidTokenError as error:
                raise HTTPUnauthorized(
                    code=error.code,
                    title="Token Verification",
                    description=error.status
                )
        raise HTTPUnauthorized(
            code=error_code,
            title="Token Verification",
            description="Invalid token, lol!"
        )

    @db_session
    def refresh_token(self, access_token, refresh_token):
        error_code = None
        for i in self._tokenizers:
            try:
                self._tokenizers[i].is_token(access_token)
            except InvalidTokenError as failure:
                error_code = failure.code
                continue
            try:
                print('refreshing token...')
                return self._tokenizers[i].refresh_token(
                    access_token, refresh_token
                )
            except InvalidTokenError as error:
                raise HTTPUnauthorized(
                    code=error.code,
                    title="Token Verification",
                    description=error.status
                )
        raise HTTPUnauthorized(
            code=error_code,
            title="Token Verification",
            description="Invalid token, lol!"
        )
