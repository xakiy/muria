"""Stats Resource."""

from muria.common.resource import Resource
from muria.db import User
from pony.orm import db_session, count
from falcon import (
    HTTP_OK,
    HTTP_NO_CONTENT
)


class UserStats(Resource):
    """Users Stats."""

    @db_session
    def on_get(self, req, resp, **params):

        user_total = count(s for s in User)

        if user_total != 0:

            resp.media = {"stats": {"type": "user", "count": user_total}}

            resp.status = HTTP_OK
        else:
            resp.status = HTTP_NO_CONTENT
