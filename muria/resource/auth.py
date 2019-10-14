"""User Resource."""

from . import Resource
import falcon
from muria.init import user_authentication, DEBUG
from muria.common.error import InvalidTokenError
from pony.orm import db_session


class Authentication(Resource):
    """
    Resource Authentication.

    Menangani otentifikasi user, termasuk mengeluarkan tokens.
    """

    @db_session
    def on_get(self, req, resp):

        resp.status = falcon.HTTP_OK
        resp.set_header("WWW-Authenticate", "Bearer")
        if DEBUG:
            resp.media = {"WWW-Authenticate": "Bearer"}

    @db_session
    def on_post(self, req, resp):
        token = user_authentication.authenticate_user(
            username=req.media.get("username", ""),
            password=req.media.get("password", "")
        )
        resp.status = falcon.HTTP_OK
        resp.media = token


class Verification(Resource):
    """
    Resource Verification

    Memverifikasi token yang dikirimkan oleh klien
    """

    def on_post(self, req, resp, **params):
        # TODO:
        # implement some cache validations on the user
        try:
            token = user_authentication.check_token(
                req.media.get("access_token")
            )
            content = {"access_token": token}
            resp.status = falcon.HTTP_200
            resp.media = content
        except InvalidTokenError as error:
            raise falcon.HTTP_BAD_REQUEST(
                code=error.code,
                description=str(error.status)
            )


class Refresh(Resource):
    def on_post(self, req, resp, **params):
        access_token = req.media.get("access_token")
        refresh_token = req.media.get("refresh_token")
        resp.media = user_authentication.refresh_token(
            access_token, refresh_token
        )
        resp.status = falcon.HTTP_OK
