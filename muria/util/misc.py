"""Miscellaneous."""

import string
import random
import uuid
from datetime import datetime, timezone

UNICODE_ASCII_CHARACTER_SET = string.ascii_letters + string.digits


def generate_chars(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for _ in range(length))


def is_uuid(uuid_string):
    try:
        return uuid.UUID(uuid_string)
    except Exception:
        return None


def get_timestamp():
    return datetime.now(tz=timezone.utc).timestamp()
