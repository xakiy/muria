"""Profile Resource."""

from muria.common.resource import Resource
from muria.db import User
from pony.orm import db_session
from falcon import (
    HTTPNotFound,
    HTTP_OK
)


class Profile(Resource):

    @db_session
    def on_get(self, req, resp):
        if req.context.user:
            resp.media = {"profile":
                User.get(id=req.context.user.get("id")).unload()}
            resp.status = HTTP_OK
        else:
            raise HTTPNotFound()
