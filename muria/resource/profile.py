"""Profile Resource."""

from muria.common.resource import Resource
from muria.db import User
from pony.orm import db_session
from pathlib import Path
from marshmallow import ValidationError
from muria.util.file import FormStore
import mimetypes
from falcon import (
    HTTPUnprocessableEntity,
    HTTPBadRequest,
    HTTPNotFound,
    HTTP_OK,
    HTTP_CREATED
)


class Profile(Resource):
    """Provide user profile retrieval and modifications."""

    @db_session
    def on_get(self, req, resp):
        if req.context.user:
            resp.media = User.get(id=req.context.user.get("id")).unload()
            resp.status = HTTP_OK

    @db_session
    def on_patch(self, req, resp):
        if req.context.user:
            user = User.get(id=req.context.user.get("id"))
            # validate submitted data
            try:
                update = user.clean(req.media, partial=("id", ))
            except ValidationError as error:
                raise HTTPUnprocessableEntity(
                    title="Profile Update Error",
                    description={"error": error.messages}
                )
            user.set(**update)
            resp.media = user.unload()
            resp.status = HTTP_OK
        else:
            raise HTTPNotFound()


class ProfilePicture(Resource):
    """Handle profile picture upload, and retrieval."""

    def __init__(self):
        self.dir_image = self.config.get("dir_image")
        self.form_store = FormStore()

    def _open_file(self, picture):
        # picture must be path-like object
        if picture.is_file():
            try:
                stream_data = open(picture, "rb")
                stream_len = picture.stat().st_size
                stream_type = mimetypes.guess_type(str(picture))[0]
                return (stream_data, stream_len, stream_type)
            except FileNotFoundError:
                pass
        # return default blank/not found picture
        return (None, None, None)

    @db_session
    def on_get(self, req, resp):
        if req.context.user:
            user = User.get(id=req.context.user.get("id"))
            if user.picture:
                profile_picture = Path(self.dir_image, user.picture)
                resp.status = HTTP_OK
                (resp.stream,
                 resp.stream_len,
                 resp.content_type) = self._open_file(profile_picture)
            else:
                raise HTTPNotFound(description="No picture found.")

    @db_session
    def on_put(self, req, resp):
        if req.context.user:
            user = User.get(id=req.context.user.get("id"))
            # TODO:
            # To prevent multiple repost, we need to use unique
            # id checking, like generated uuid that will be
            # compared to previous post
            # uid = req.get_param('profile_image_id')
            profile_image = req.context.files.get("profile_picture")

            if profile_image is not None:
                name = self.form_store.save(profile_image, self.dir_image)
                if name is not None:
                    if user.picture is not None:
                        self.form_store.delete(user.picture)
                    user.picture = name
                    # resp.media = {"upload": "{0} ok.".format(name)}
                    resp.location = req.uri
                    resp.status = HTTP_CREATED
                else:
                    raise HTTPUnprocessableEntity(description="Upload failed.")
            else:
                raise HTTPBadRequest(description="Upload no file error")
