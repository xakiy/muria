import time
import uuid
import hashlib
import binascii
from os import urandom
from datetime import date
from .mixin import EntityMixin
from pony.orm import (
    Database,
    PrimaryKey,
    Required,
    Optional,
    Set,
    Discriminator,
)


db = connection = Database()


class User(db.Entity, EntityMixin):
    # We store uuid in string column instead of binary
    # to simplify object instantiation and lookup
    id = PrimaryKey(str, 36, default=str(uuid.uuid4()))
    nama = Required(str)
    jinshi = Optional(str, 1)
    tempat_lahir = Optional(str, 60)
    tanggal_lahir = Optional(date)
    tanggal_masuk = Optional(date, default=lambda: date.today())
    username = Required(str, 40, unique=True)
    situs = Optional(str, default="")
    email = Required(str, 60, unique=True)
    password = Required(str)
    salt = Required(str)
    suspended = Required(bool, default=False)
    basic_tokens = Set("BasicToken")
    clients = Set("Client")
    grants = Set("Grant")

    def get_user_id(self):
        return self.id

    @staticmethod
    def hash_password(string, salt):
        salt_bin = salt
        digest = hashlib.sha256(bytes(string, "utf8")).digest()
        hashed_bin = hashlib.sha256(digest).digest()
        hashed_bin_key = hashlib.pbkdf2_hmac(
            "sha256", hashed_bin, salt_bin, 1000
        )
        return hashed_bin_key.hex()

    @classmethod
    def create_salted_password(cls, password):
        """Create new password based on supplied digest.
        Args:
            password_string: plain string.
        Return tuple of hex version of the salt and the password.
        """
        salt_bin = urandom(20)
        return salt_bin.hex(), cls.hash_password(password, salt_bin)

    def check_password(self, password):
        salt_bin = binascii.unhexlify(self.salt)
        return self.password == self.hash_password(password, salt_bin)


class Client(db.Entity):

    GRANT_TYPES = {
        ('authorization_code', 'Authorization Code'),
        ('implicit', 'Implicit'),
        ('password', 'Resource Wwner Password Credentials'),
        ('client_credentials', 'Client Credentials')
    }

    id = PrimaryKey(int, size=64, auto=True)
    user = Required("User")
    grant = Optional("Grant")
    client_id = Required(str, 48, index=True)
    client_secret = Optional(str, 120, index=True, unique=True)
    name = Required(str, 100)
    _redirect_uris = Optional(str)
    _default_scope = Optional(str, default="profile")
    grant_type = Required(str, default="password")
    is_confidential = Required(bool, default=False)

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0] if self.redirect_uris else None

    @property
    def allowed_grant_types(self):
        return [id for id, name in self.GRANT_TYPES]

    @property
    def redirect_uris(self):
        return self._redirect_uris.split(",")

    @property
    def default_scopes(self):
        return self._default_scopes.split()


class BasicToken(db.Entity, EntityMixin):
    _discriminator_ = "basic"
    id = PrimaryKey(int, size=64, auto=True)
    token_type = Discriminator(str)
    access_token = Required(str, 255, unique=True, index=True)
    refresh_token = Optional(str, 255, index=True)
    revoked = Required(bool, default=False)
    issued_at = Optional(int, default=lambda: int(time.time()))
    expires_in = Optional(int, default=0)
    scope = Optional(str, default="")
    user = Required("User")

    def is_revoked(self):
        return self.revoked

    def get_expires_in(self):
        return self.expires_in

    def get_expires_at(self):
        return self.issued_at + self.expires_in

    def is_refresh_token_expired(self):
        expired_at = self.issued_at + self.expires_in * 5
        return expired_at < time.time()

    @property
    def user_id(self):
        return self.user.get_user_id()

    @property
    def scopes(self):
        return self.scope.split() if self.scope else None

    def is_valid(self, scopes=None):
        return not self.is_expired() and self.allow_scopes(scopes)

    def is_expired(self):
        return time.time() >= self.get_expires_at()

    def allow_scopes(self, scopes):
        if not scopes:
            return True

        provided_sopes = set(self.scope.split())
        resource_scopes = set(scopes)

        return resource_scopes.issubset(provided_sopes)


class Grant(db.Entity):
    user = Required("User")
    client = Required("Client")
    code = Required(str, index=True)
    redirect_uri = Optional(str)
    scope = Optional(str)
    issued_at = Optional(int, default=lambda: int(time.time()))
    expires_in = Optional(int, default=0)

    @property
    def scopes(self):
        return self.scope.split() if self.scope else None
