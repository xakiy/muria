"""Account Resource."""

from . import Resource
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


class Accounts(Resource):

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
                    "accounts": [
                        schema.dump(account.to_dict()) for account in query
                    ]
                }
                resp.status = HTTP_OK
            else:
                raise HTTPNotFound()
        else:
            max_limit = self.config.getint("app", "page_limit")

            offset = req.params.get("index", 0)
            limit = max_limit if req.params.get("count", 10) > max_limit else 10

            accounts = User.select()[offset:limit]
            schema = _User()
            found = len(accounts)
            if found > 0:
                resp.media = {
                    "count": found,
                    "accounts": [
                        schema.dump(account.to_dict()) for account in accounts
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
                title="Account Update Error",
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


class AccountDetail(Resource):

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
                    title="Account Update Error",
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
                    title="Account Delete Error"
                )
            flush()
            resp.media = deleted
            resp.status = HTTP_GONE
        else:
            raise HTTPNotFound()
