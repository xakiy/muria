"""Miscellaneous."""

import hashlib
import string
import random
import uuid
import base64


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


def extract_auth_header(auth_string, auth='basic'):
    # currently only support basic and bearer
    types = ('basic', 'bearer')
    if auth not in types:
        auth = 'basic'
    # extracting string like 'Basic am9objpzZWNyZXQ='
    encoded = auth_string.partition(auth.title())[2].strip()
    if not len(encoded) > 0:
        return "", ""
    if not isinstance(encoded, bytes):
        encoded = bytes(encoded, 'utf8')
    decoded = base64.urlsafe_b64decode(encoded).decode('utf8')
    # return list of username and password
    return decoded.split(':')
