"""Tokenizers."""

import jwt
import time
from datetime import datetime, timedelta
from calendar import timegm
from muria.db.model import User, BasicToken
from pony.orm import db_session
from strgen import StringGenerator as _generator
from muria.common.error import (
    InvalidTokenError,
    TokenExpiredError,
    TokenRevokedError,
    InvalidRefreshTokenError,
    RefreshTokenExpiredError
)


class BaseToken(object):
    """Base Token."""

    TOKEN_TYPE = None
    TOKEN_NAME = None

    def create_payload(self, username, **params):
        pass

    def create_token(self, payload, username):
        raise NotImplementedError()

    def verify_token(self, token):
        raise NotImplementedError()

    def refresh_token(self, access_token, refresh_token):
        raise NotImplementedError()

    def is_token(self, token):
        raise NotImplementedError()


class TokenBasic(BaseToken):
    """Token with basic generated code."""

    TOKEN_TYPE = "basic"
    TOKEN_NAME = "token_basic"

    def __init__(self, config, token_refresh_expire=4):
        self.config = config
        self.token_basic_length = config.getint(
            'security', 'token_basic_length'
        )
        self.token_refresh_length = self.token_basic_length + 4
        self.token_expire = config.getint("security", "access_token_exp")

    def _generate_token(self, digit=0):
        length = digit if digit > 0 else \
            self.token_basic_length
        # strgen '\w' is equivalent with identifier in str
        template = '[\\w]{' + str(length) + '}'
        return _generator(template).render()

    @db_session
    def create_token(self, payload, username):
        user = User.get(username=username)
        if user:
            access_token = self._generate_token()
            refresh_token = self._generate_token(self.token_refresh_length)

            token = BasicToken(
                token_type=self.TOKEN_TYPE,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self.token_expire,
                user=user
            )
            return token.to_dict()

    @db_session
    def verify_token(self, token, allow_expired=False):
        """Verify given token and return it if it's valid."""

        self.is_token(token)

        basic_token = BasicToken.get(
            access_token=token,
            token_type=self.TOKEN_TYPE
        )
        if basic_token is None:
            # token is received but unable to process due to
            # invalid content
            raise InvalidTokenError()

        if not allow_expired:
            if basic_token.get_expires_at() <= time.time():
                raise TokenExpiredError()

        if basic_token.is_revoked():
            raise TokenRevokedError()

        return basic_token.access_token

    def refresh_token(self, access_token, refresh_token):
        self.is_token(access_token)

        old_token = BasicToken.get(
            access_token=access_token,
            token_type=self.TOKEN_TYPE
        )
        if old_token is None:
            # token is received but unable to process due to
            # invalid content
            raise InvalidTokenError()

        if old_token.get_expires_at() <= time.time():
            raise TokenExpiredError()

        if old_token.is_revoked():
            raise TokenRevokedError()

        if old_token.refresh_token != refresh_token:
            raise InvalidRefreshTokenError()

        if old_token.is_refresh_token_expired():
            raise RefreshTokenExpiredError()

        new_token = self.create_token(None, old_token.user.username)
        old_token.revoked = True
        return new_token

    def is_token(self, token):
        length = len(token) == self.token_basic_length
        if length and token.isidentifier():
            return True
        raise InvalidTokenError()


class TokenJWT(BaseToken):

    TOKEN_TYPE = "jwt"
    TOKEN_NAME = "token_jwt"

    def __init__(self, config, ecdsa=True, rsa=False):
        self.config = config
        self.private_key = config.getbinary("security", "private_key")
        self.public_key = config.getbinary("security", "public_key")
        self.algorithm = config.get("security", "algorithm")
        self.token_issuer = config.get("security", "issuer")
        self.token_audience = config.get("security", "audience")
        self.access_token_exp = config.getint("security", "access_token_exp")
        self.refresh_token_exp = config.getint("security", "refresh_token_exp")

    @db_session
    def create_payload(self, username, **params):
        user = User.get(username=username)
        payload = {
            "name": user.orang.nama,
            "pid": str(user.orang.id),
            "roles": [x for x in user.kewenangan.wewenang.nama],
        }
        return payload

    def create_token(self, payload, username):
        # JWT Reserved Claims
        # Claims    name          Format         Usage
        # -------   ----------    ------         ---------
        # ‘exp’     Expiration    int            The time after which the token is invalid.
        # ‘nbf’     Not before    int            The time before which the token is invalid.
        # ‘iss’     Issuer        str            The principal that issued the JWT.
        # ‘aud’     Audience      str/list(str)  The recipient that the JWT is intended for.
        # ‘iat’     Issued At     int            The time at which the JWT was issued.

        # The time values will be converted automatically into int if it populated with datetime object.

        tokens = {}
        now = datetime.utcnow()
        access_token_default_claims = {
            "iss": self.token_issuer,
            "aud": self.token_audience,
            "iat": now,
            "exp": now + timedelta(seconds=self.access_token_exp),
        }
        access_token_payload = payload.copy()
        access_token_payload.update(access_token_default_claims)

        tokens["access_token"] = jwt.encode(
            access_token_payload, self.private_key, algorithm=self.algorithm
        )

        acc_token_sig = bytes(tokens["access_token"]).decode("utf8")

        refresh_token_payload = {
            "tsig": acc_token_sig.split(".")[2],
            # decode this unixtimestamp using datetime.utcfromtimestamp()
            "tiat": timegm(now.utctimetuple()),
            "iss": self.token_issuer,
            "aud": self.token_audience,
            "iat": now,
            "exp": now + timedelta(seconds=self.refresh_token_exp),
        }
        tokens["refresh_token"] = jwt.encode(
            refresh_token_payload, self.private_key, algorithm=self.algorithm
        )
        content = {
            # some clients do not recognize the token type if
            # not properly titled case as in RFC6750 section-2.1
            "token_type": "Bearer",
            "expires_in": self.config.getint(
                "security", "access_token_exp"
            ),
            "refresh_token": tokens["refresh_token"],
            "access_token": tokens["access_token"],
        }

        # TODO:
        # Store content first in database before sending it out
        return content

    def verify_token(self, access_token):
        self.is_token(access_token)

        try:
            jwt.decode(
                access_token,
                key=self.public_key,
                algorithms=self.algorithm,
                issuer=self.token_issuer,
                audience=self.token_audience,
            )
            return access_token
        except jwt.InvalidTokenError as error:
            # token is received but unable to process due to
            # invalid content or invalid signature
            raise InvalidTokenError(status=str(error))

    def refresh_token(self, access_token, refresh_token):
        # on success this will return pair of refreshed
        # access token and refresh token, otherwise it
        # will return tuple of error code

        self.is_token(access_token)

        acc_token_sig = access_token.split(".")[2]
        try:
            token_payload = jwt.decode(
                access_token,
                key=self.public_key,
                algorithms=self.algorithm,
                issuer=self.token_issuer,
                audience=self.token_audience,
                options={"verify_exp": False},
            )
        except jwt.InvalidTokenError as error:
            raise InvalidTokenError(status=str(error))

        try:
            refresh_payload = jwt.decode(
                refresh_token,
                key=self.public_key,
                algorithms=self.algorithm,
                issuer=self.token_issuer,
                audience=self.token_audience,
            )
        except jwt.ExpiredSignatureError as error:
            raise RefreshTokenExpiredError(status=str(error))

        if acc_token_sig != refresh_payload["tsig"]:
            raise InvalidRefreshTokenError(status="Token Pair Mismatch")
        return self.create_token(token_payload)

    def is_token(self, token):
        if isinstance(token, str) and token.count(".") == 2:
            return True
        raise InvalidTokenError()
