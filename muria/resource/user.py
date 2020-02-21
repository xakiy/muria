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
from marshmallow import ValidationError


class Users(Resource):

    @db_session
    def on_get(self, req, resp, **params):
        """List of users.
        ---
        tags:
        - user
        summary: List of users
        description: Get list of users
        operationId: listUsers
        produces:
        - application/json
        parameters:
            - in: header
              name: origin
              type: string
              required: true
              description: CORS request origin
            - in: header
              name: authorization
              type: string
              required: true
              description: Auth token
            - in: query
              name: search
              type: string
              required: false
              description: Search user based on their username
        responses:
            200:
                description: List of registered users
                schema:
                  type: object
                  properties:
                    count:
                      type: integer
                    users:
                      type: array
                      items:
                        $ref: '#/definitions/User'
            404:
                description: No user found
        """

        max_limit = self.config.getint("api_pagination_limit")
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
            resp.media = {
                "count": found,
                "users": [
                    user.unload() for user in users
                ]
            }
            resp.status = HTTP_OK
        else:
            raise HTTPNotFound()

    @db_session
    def on_post(self, req, resp, **params):
        """Add new user.
        ---
        tags:
        - user
        summary: Add new user
        description: Add new additional user
        operationId: addUser
        consumes:
        - application/json
        produces:
        - application/json
        parameters:
            - in: header
              name: origin
              type: string
              required: true
              description: CORS request origin
            - in: body
              name: user
              required: true
              description: user data
              schema: User
        responses:
            201:
                description: User added successfully
                schema: User
            400:
                description: Bad request dou to bad parameters
            409:
                description: Conflicted, user already exist
            422:
                description: Unprocessable, invalids params found
            500:
                description: Internal service error
        """

        if not req.media:
            raise HTTPBadRequest()

        try:
            data = User.clean(req.media, partial=("id",))
        except ValidationError as error:
            raise HTTPUnprocessableEntity(
                title="User Update Error",
                description={"error": error.messages}
            )

        # this will prevent data duplication but seems
        # it will take some times
        if User.exists(username=data["username"], email=data["email"]):
            raise HTTPConflict()

        try:
            user = User(**data)
            flush()
            resp.media = user.unload()
            resp.status = HTTP_CREATED
        except Exception:
            # TODO: log here internally
            # this would rarely hit
            raise HTTPInternalServerError(description="Database Error")


class UserDetail(Resource):

    @db_session
    def on_get(self, req, resp, id, **params):
        """Get specifig user based on their id.
        ---
        tags:
        - user
        summary: Show user data
        description: Get specific user information
        operationId: getUser
        consumes:
        - application/json
        produces:
        - application/json
        parameters:
            - in: header
              name: origin
              type: string
              required: true
              description: CORS request origin
            - in: path
              name: id:uuid
              required: true
              type: string
              format: uuid
              description: user id in uuid format
        responses:
            200:
                description: Data of registered user
                schema: User
            404:
                description: No user found
        """
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
        """Edit user data
        ---
        tags:
        - user
        summary: Edit user data
        description: Modify registered user data
        operationId: editUser
        consumes:
        - application/json
        produces:
        - application/json
        parameters:
            - in: header
              name: origin
              type: string
              required: true
              description: CORS request origin
            - in: path
              name: id:uuid
              type: string
              format: uuid
              required: true
            - in: body
              name: user
              required: true
              description: user data
              schema: User
        responses:
            200:
                description: User aditted successfully
            404:
                description: No user found
            422:
                description: Unprocessable, invalids params found
        """
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
        """Edit user data
        ---
        tags:
        - user
        summary: Delete user
        description: Delete specific user based on their ID
        operationId: delUser
        produces:
        - application/json
        parameters:
            - in: header
              name: origin
              type: string
              required: true
              description: CORS request origin
            - in: path
              name: id:uuid
              type: string
              format: uuid
              required: true
        responses:
            404:
                description: No user found
            410:
                description: Gone, user deleted successfully
                schema: User
            422:
                description: Unprocessable, invalids params found
        """

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
