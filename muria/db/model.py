import time
import uuid
import hashlib
import binascii
from os import urandom
from datetime import date, datetime
from .mixin import EntityMixin
from pony.orm import (
    PrimaryKey,
    Required,
    Optional,
    Set,
    Discriminator,
    LongStr
)


def define_entities(db):

    class User(db.Entity, EntityMixin):
        # We store uuid in string column instead of binary
        # to simplify object instantiation and lookup
        _table_ = "users"
        id = PrimaryKey(str, 36, default=lambda: str(uuid.uuid4()))
        nama = Required(str)
        jinshi = Optional(str, 1)
        tempat_lahir = Optional(str, 60)
        tanggal_lahir = Optional(date)
        tanggal_masuk = Optional(date, default=lambda: date.today())
        username = Required(str, 40, unique=True)
        situs = Optional(str, default="")
        picture = Optional(str, nullable=True)
        email = Required(str, 60, unique=True)
        password = Required(str)
        salt = Optional(str)
        suspended = Required(bool, default=False)
        roles = Set("Role")
        tokens = Set("BaseToken")

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

        @classmethod
        def authenticate(cls, username, password):
            user = cls.get(username=username)
            if user and user.check_password(password):
                return user
            else:
                return None

        def before_insert(self):
            self.salt, self.password = self.create_salted_password(self.password)

        def get_roles(self):
            # self.responsibilities
            return [role.name for role in self.roles]

    class BaseToken(db.Entity):
        _discriminator_ = "base"
        id = PrimaryKey(int, size=64, auto=True)
        token_type = Discriminator(str)
        access_token = Required(LongStr)
        refresh_token = Optional(LongStr)
        revoked = Required(bool, default=False)
        issued_at = Optional(float, default=datetime.utcnow().timestamp)
        expires_in = Optional(int, default=300)
        refresh_expires_in = Optional(int, default=300 * 15)
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

    class JwtToken(BaseToken, EntityMixin):
        _discriminator_ = "jwt"
        # these access_key and refresh_key indexes is a workaround
        # for LongStr full-text index key constraints
        access_key = Required(str, 43, unique=True, index=True)
        refresh_key = Optional(str, 43, unique=True, index=True)

    class Role(db.Entity):
        id = PrimaryKey(int, auto=True)
        name = Required(str)
        info = Optional(str)
        contexts = Set("Responsibility")
        users = Set("User")

    class Responsibility(db.Entity):
        id = PrimaryKey(int, auto=True)
        name = Required(str, unique=True)
        info = Optional(str, nullable=True)
        roles = Set("Role")
