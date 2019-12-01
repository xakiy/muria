"""User Resource."""
# NOTE: This resource is intended for super admin only,
#       for personal user info please see profile resource.

from muria.common.resource import Resource
from muria.db import User
from pony.orm import db_session, flush
from falcon import (
    HTTPNotFound,
    HTTPBadRequest,
    HTTPConflict,
    HTTPInternalServerError,
    HTTPUnprocessableEntity,
    HTTP_OK,
    HTTP_GONE,
    HTTP_CREATED
)
from muria.db.schema import _User
from marshmallow import ValidationError


class Users(Resource):

    @db_session
    def on_get(self, req, resp, **params):

        max_limit = self.config.getint("app", "page_limit")
        count = int(req.params.get("count", 20))

        offset = int(req.params.get("index", 0))
        limit = max_limit if count > max_limit else 20

        if req.params.get("search") is not None:
            users = User.select(
                lambda user: req.params.get("search") in user.username
            )[offset:limit]
        else:
            users = User.select()[offset:limit]

        found = len(users)
        if found > 0:
            schema = _User()
            resp.media = {
                "count": found,
                "users": [
                    schema.dump(user.to_dict()) for user in users
                ]
            }
            resp.status = HTTP_OK
        else:
            raise HTTPNotFound()

    @db_session
    def on_post(self, req, resp, **params):

        if not req.media:
            raise HTTPBadRequest()

        _user = _User()

        try:
            data = _user.load(req.media, partial=("id",))
        except ValidationError as error:
            raise HTTPUnprocessableEntity(
                title="User Update Error",
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
        except Exception:
            # this would rarely hit
            raise HTTPInternalServerError(description="Database Error")


class UserDetail(Resource):

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
                    title="User Update Error",
                    description={"error": error.messages}
                )
            user.set(**update)
            flush()
            resp.media = user.unload()
            resp.status = HTTP_OK
        else:
            raise HTTPNotFound()

    @db_session
    def on_delete(self, req, resp, id, **params):

        # NOTE: Secure this endpoint so that only privileged user is allowed
        id = str(id)
        if User.exists(id=id):

            user = User.get(id=id)
            try:
                deleted = user.unload()
                user.delete()
            except Exception:
                # this might cought either pony or marshmallow exception
                raise HTTPUnprocessableEntity(
                    title="User Delete Error"
                )
            flush()
            resp.media = deleted
            resp.status = HTTP_GONE
        else:
            raise HTTPNotFound()
