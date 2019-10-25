"""Profile Resource."""

from . import Resource
from muria.db import User
from pony.orm import db_session, flush
from muria.util.misc import is_uuid
from falcon import (
    HTTPNotFound,
    HTTP_OK,
    HTTPUnprocessableEntity
)
from marshmallow import ValidationError


class Profile(Resource):

    @db_session
    def on_get(self, req, resp, **params):

        id = req.params.get("id", "")
        if not is_uuid(id):
            raise HTTPNotFound()

        if User.exists(id=id):
            resp.media = User.get(id=id).unload()
            resp.status = HTTP_OK
        else:
            raise HTTPNotFound()

    @db_session
    def on_patch(self, req, resp, **params):
        id = req.media.get("id", "")
        if is_uuid(id) and User.exists(id=id):

            user = User.get(id=id)
            # validate submitted data
            try:
                update = user.clean(req.media)
            except (TypeError, ValidationError) as error:
                raise HTTPUnprocessableEntity(
                    title="Profile Update Error",
                    description={"error": error.messages}
                )

            user.set(**update)
            flush()
            resp.media = user.unload()
            resp.status = HTTP_OK
        else:
            raise HTTPNotFound()
