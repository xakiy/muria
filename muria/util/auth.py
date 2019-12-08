"""User Authentication Factory."""

from muria.db.model import Client, User, BearerToken, Grant
from muria.db.schema import Credentials
from pony.orm import db_session
from muria.util.token import (
    TokenBearer,
    TokenJWT,
    InvalidTokenError
)
from falcon import (
    HTTPUnprocessableEntity,
    HTTPUnauthorized
)


class Authentication(object):
    """Authenticate user based on username and password."""

    def __init__(self, config):

        self.login_schema = Credentials()
        token_bearer = TokenBearer(config)
        token_jwt = TokenJWT(config)
        self._tokenizers = {'bearer': token_bearer, 'jwt': token_jwt}
        # self.tokenizer = self._tokenizers['bearer']

    def validate(self, credentials):
        return self.login_schema.validate(credentials)

    @db_session
    def authenticate_user(self, username, password, token_type='bearer'):
        """Authenticate user with their username and password."""

        self.tokenizer = self._tokenizers.get(token_type)
        credentials = {"username": username, "password": password}
        errors = self.validate(credentials)
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

    @db_session
    def get_token_owner(self, token):
        return self.get_token_owner_attr(token, attr=("user_id"))

    @db_session
    def get_token_owner_attr(self, token, attr=("user_id")):
        data = {}
        failure = None
        for i in self._tokenizers:
            try:
                data = self._tokenizers[i].get_token_owner_attr(token, attr)
                break
            except InvalidTokenError as error:
                failure = error
                continue

        if data:
            return data
        else:
            raise HTTPUnauthorized(
                code=failure.code,
                title="Token Verification",
                description=failure.status
            )

    @db_session
    def get_client(self, client_id):
        return Client.get(client_id=client_id)

    @db_session
    def get_user(self, username, password, client, *args, **kwargs):
        """Get user with their username and password."""

        if not client.allowed_grant_types == 'password':
            return None

        credentials = {"username": username, "password": password}
        errors = self.validate(credentials)
        if errors:
            raise HTTPUnprocessableEntity(
                code=88810,  # unprocessable creds either blank or invalid
                title="Authentication Failure",
                description=str(errors)
            )
        user = User.get(username=credentials["username"])
        if user and user.check_password(credentials["password"]):
            return user
        else:
            return None

    @db_session
    def get_token(self, access_token=None, refresh_token=None):
        if access_token:
            return BearerToken.get(
                access_token=access_token,
                token_type='bearer'
            )
        if refresh_token:
            return BearerToken.get(
                refresh_token=refresh_token,
                token_type='bearer'
            )
        return None

    @staticmethod
    def set_token(token, request, *args, **kwargs):
        """save token."""
        if request.client and request.user:
            if request.client.client_id == request.user.client.client_id:
                data = token.update({'user': request.user})
            if not BearerToken.exists(**data):
                BearerToken(**data)

    def get_grant(client_id, code):
        client = Client.get(client_id=client_id)
        return Grant.get(client=client, code=code)

    def set_grant(client_id, code, request, *args, **kwargs):
        if client_id and code and request.user:

            client = Client.get(client_id=client_id)
            grant = {
                'client': client,
                'code': code,
                'user': request.user,
                'scope': request.scope,
                'expires_in': 300
            }
            if not Grant.exists(**grant):
                Grant(**grant)
