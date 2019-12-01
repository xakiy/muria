"""User Resource."""

from muria.common.resource import Resource
from muria.init import user_authentication, DEBUG
from pony.orm import db_session
from muria.util.tokenizer import extract_auth_header
from falcon import (
    HTTP_OK,
    HTTPBadRequest
)


class Authentication(Resource):
    """
    Resource Authentication.

    Menangani otentifikasi user, termasuk mengeluarkan tokens.
    """

    @db_session
    def on_get(self, req, resp):

        resp.status = HTTP_OK
        resp.set_header("WWW-Authenticate", "Bearer")
        if DEBUG:
            resp.media = {"WWW-Authenticate": "Bearer"}

    @db_session
    def on_post(self, req, resp):
        if req.media:
                token = user_authentication.authenticate_user(
                    username=req.media.get("username", ""),
                    password=req.media.get("password", "")
                )
        elif req.headers.get("AUTHORIZATION"):
            username, password = extract_auth_header(
                req.headers.get("AUTHORIZATION", "")
            )
            token = user_authentication.authenticate_user(
                username=username,
                password=password
            )
        else:
            raise HTTPBadRequest()

        resp.status = HTTP_OK
        resp.media = token


class Verification(Resource):
    """
    Resource Verification

    Memverifikasi token yang dikirimkan oleh klien
    """

    def on_post(self, req, resp, **params):
        # TODO:
        # implement some cache validations on the user

        if req.media:
            token = user_authentication.check_token(
                req.media.get("access_token", "")
            )
            content = {"access_token": token}
            resp.status = HTTP_OK
            resp.media = content
        else:
            raise HTTPBadRequest()


class Refresh(Resource):
    def on_post(self, req, resp, **params):
        if req.media:
            access_token = req.media.get("access_token", "")
            refresh_token = req.media.get("refresh_token", "")
            resp.media = user_authentication.refresh_token(
                access_token, refresh_token
            )
            resp.status = HTTP_OK
        else:
            raise HTTPBadRequest()
