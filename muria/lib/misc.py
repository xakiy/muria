"""Miscellaneous."""

import datetime
import hashlib
import string
import random
import uuid


UNICODE_ASCII_CHARACTER_SET = string.ascii_letters + string.digits

try:
    import rapidjson as json
except ImportError:
    import json

    class ConvertionEncoder(json.JSONEncoder):
        def default(self, obj):
            """Mengubah datetime sebagai string biasa."""
            if isinstance(obj, datetime.datetime) or \
                    isinstance(obj, datetime.date):
                return obj.isoformat()[:10]

            """Mengubah bytes menjadi string biasa."""
            if isinstance(obj, bytes):
                return obj.decode()

            """Abaikan bila sebuah dict."""
            if isinstance(obj, dict):
                return

            try:
                return json.JSONEncoder.default(self, obj)
            except TypeError:
                return str(obj)


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


def dumpAsJSON(source):
    """Mengubah dict JSON.

    NOTE: All date type is dumped in ISO8601 format
    """
    if json.__name__ == "rapidjson":
        # UM_NONE = 0,
        # UM_CANONICAL = 1<<0 like
        # 4-dashed 32 hex chars: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        # UM_HEX = 1<<1 // canonical OR 32 hex chars in a row
        # pure JSON
        output = json.dumps(
            source, datetime_mode=json.DM_ISO8601, uuid_mode=json.UM_CANONICAL
        )  # speed 1.8xx
    elif json.__name__ == 'json':
        # pure JSON
        # output = rjson.dumps(source, default=datetimeToISO) # speed 1.6xx
        # output = ujson.dumps(source)
        output = json.dumps(source, cls=ConvertionEncoder)  # speed 1.8xx
        # output = sjson.dumps(sjson.loads(source), use_decimal=False)
        # output = json.dumps(source) #not work for datetime.date field

    return output


def is_uuid(uuid_string):
    try:
        return uuid.UUID(uuid_string)
    except Exception:
        return None
