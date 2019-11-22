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
    basic_token = Set("BasicToken")

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


class BasicToken(db.Entity, EntityMixin):
    id = PrimaryKey(int, size=64, auto=True)
    token_type = Discriminator(str)
    _discriminator_ = "basic"
    access_token = Required(str, 255, unique=True, index=True)
    refresh_token = Optional(str, 255, index=True)
    revoked = Required(bool, default=False)
    issued_at = Optional(int, default=lambda: int(time.time()))
    expires_in = Optional(int, default=0)
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
