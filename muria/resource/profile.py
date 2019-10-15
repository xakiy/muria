"""Profile Resource."""

from . import Resource
from muria.db import Bio
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

        if Bio.exists(id=id):
            resp.media = Bio.get(id=id).unload()
            resp.status = HTTP_OK
        else:
            raise HTTPNotFound()

    @db_session
    def on_patch(self, req, resp, **params):
        id = req.media.get("id", "")
        if is_uuid(id) and Bio.exists(id=id):

            profile = Bio.get(id=id)
            # validate submitted data
            try:
                update = profile.clean(req.media)
            except ValidationError as error:
                raise HTTPUnprocessableEntity(
                    title="Profile Update Error",
                    description={"error": error.messages}
                )

            profile.set(**update)
            flush()
            resp.media = profile.unload()
            resp.status = HTTP_OK
        else:
            raise HTTPNotFound()
