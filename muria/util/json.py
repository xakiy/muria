"""Custom JSON Handler."""

from falcon import media
from functools import partial
import datetime


try:
    import orjson as json
except ImportError:
    try:
        import rapidjson as json
    except ImportError:
        import json


if json.__name__ == "orjson":
    # OPT_STRICT_INTEGER = 1
    # OPT_SERIALIZE_UUID = 32
    json_dumper = partial(
        json.dumps,
        option=json.OPT_SERIALIZE_UUID | json.OPT_STRICT_INTEGER)
    json_loader = json.loads

if json.__name__ == "rapidjson":
    # UM_NONE = 0,
    # UM_CANONICAL = 1<<0, // UUID in plain 32 hex chars
    # UM_HEX = 1<<1 // canonical OR 32 hex chars in a row
    json_dumper = partial(
        json.dumps,
        datetime_mode=json.DM_ISO8601,
        uuid_mode=json.UM_CANONICAL)
    json_loader = json.loads

elif json.__name__ == "json":
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
    json_dumper = partial(json.dumps, cls=ConvertionEncoder)
    json_loader = json.loads

JSONHandler = media.JSONHandler(dumps=json_dumper, loads=json_loader)


def dumpAsJSON(source):
    """Mengubah dict JSON.

    NOTE: All date type is dumped in ISO8601 format
    """
    return json_dumper(source)
