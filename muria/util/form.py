"""Form Handler for X-WWW-FORM-URLENCODED."""

from urllib import parse
from falcon import (
    errors,
    media,
    uri
)


class FormHandler(media.BaseHandler):
    """Custom Handler for 'application/x-www-form-urlencoded'."""

    def deserialize(self, stream, content_type, content_length):
        """Deserialize stream."""
        if content_length > 0:
            try:
                return uri.parse_query_string(stream.read().decode("utf-8"))
            except ValueError as err:
                raise errors.HTTPBadRequest(
                    "Invalid Form field",
                    "Could not parse field content - {0}".format(err),
                )

    def serialize(self, media, content_type):
        """Serialize data."""
        result = parse.urlencode(media)
        if not isinstance(result, bytes):
            return result.encode("utf-8")
        return result
