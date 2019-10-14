"""Miscellaneous."""

import hashlib
import string
import random
import uuid


UNICODE_ASCII_CHARACTER_SET = string.ascii_letters + string.digits


def generate_chars(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for _ in range(length))


def getEtag(content):
    """Hitung entity tag."""
    tag = "W/"  # Weak eTag
    if len(content) == 0:
        return tag + '"d41d8cd98f00b204e9800998ecf8427e"'
    else:
        hashed = hashlib.md5(bytes(content, "utf8")).hexdigest()
        return tag + '"' + hashed + '"'


def is_uuid(uuid_string):
    try:
        return uuid.UUID(uuid_string)
    except Exception:
        return None
