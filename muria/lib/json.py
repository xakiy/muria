"""Custom JSON Handler."""

from falcon import media
from functools import partial
import datetime

try:
    import rapidjson as json
except ImportError:
    import json

    class ConvertionEncoder(json.JSONEncoder):
        """JSON standard lib encoder."""

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


# NOTE: All date type is dumped in ISO8601 format
if json.__name__ == "rapidjson":
    # UM_NONE = 0,
    # UM_CANONICAL = 1<<0, // 4-dashed 32 hex chars: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    # UM_HEX = 1<<1 // canonical OR 32 hex chars in a row
    JSONHandler = media.JSONHandler(
        dumps=partial(
            json.dumps,
            datetime_mode=json.DM_ISO8601,
            uuid_mode=json.UM_CANONICAL
        ),
        loads=json.loads
    )
else:
    JSONHandler = media.JSONHandler(
        dumps=partial(
            json.dumps,
            cls=ConvertionEncoder
        ),
        loads=json.loads
    )
