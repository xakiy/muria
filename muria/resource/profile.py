"""Profile Resource."""

from . import Resource
from muria.db import User
from pony.orm import db_session, flush
from muria.util.misc import is_uuid
from falcon import (
    HTTPNotFound,
    HTTPBadRequest,
    HTTPConflict,
    HTTPUnprocessableEntity,
    HTTP_OK,
    HTTP_CREATED
)
from muria.db.schema import _User
from marshmallow import ValidationError


class Profiles(Resource):

    @db_session
    def on_get(self, req, resp, **params):

        if req.params.get("search") is not None:
            schema = _User()
            query = User.select(
                lambda user: req.params.get("search") in user.username
            )
            if query.count() > 0:
                resp.media = {
                    "count": query.count(),
                    "profiles": [
                        schema.dump(profile.to_dict()) for profile in query
                    ]
                }
                resp.status = HTTP_OK
            else:
                raise HTTPNotFound()
        else:
            max_limit = self.config.getint("app", "page_limit")

            offset = req.params.get("index", 0)
            limit = max_limit if req.params.get("count", 10) > max_limit else 10

            profiles = User.select()[offset:limit]
            schema = _User()
            found = len(profiles)
            if found > 0:
                resp.media = {
                    "count": found,
                    "profiles": [
                        schema.dump(profile.to_dict()) for profile in profiles
                    ]
                }
                resp.status = HTTP_OK
            else:
                raise HTTPNotFound()

    @db_session
    def on_post(self, req, resp, **params):

        if not req.media:
            raise HTTPNotFound()

        _user = _User()

        try:
            data = _user.load(req.media, partial=("id",))
        except ValidationError as error:
            raise HTTPUnprocessableEntity(
                title="Profile Update Error",
                description={"error": error.messages}
            )

        # this will prevent data duplication but seems
        # it will take some times
        password = data.pop('password')
        if User.exists(**data):
            raise HTTPConflict()

        try:
            data['salt'], data['password'] = \
                User.create_salted_password(password)
            user = User(**data)
            flush()
            resp.media = user.unload()
            resp.status = HTTP_CREATED
        except Exception as error:
            raise HTTPBadRequest()


class ProfileDetail(Resource):

    @db_session
    def on_get(self, req, resp, id, **params):
        id = str(id)
        if User.exists(id=id):
            resp.media = User.get(id=id).unload()
            resp.status = HTTP_OK
        else:
            raise HTTPNotFound()

    @db_session
    def on_patch(self, req, resp, id, **params):
        # make sure that we use {id:uuid} in the route
        # so that invalid uuid won't reach here
        id = str(id)
        if User.exists(id=id):

            user = User.get(id=id)
            # validate submitted data
            try:
                update = user.clean(req.media, partial=("id", ))
            except ValidationError as error:
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
