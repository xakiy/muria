"""Authentication Resource."""

from muria.common.resource import Resource
from falcon import (
    HTTP_SERVICE_UNAVAILABLE,
    HTTPMissingParam,
    HTTPBadRequest
)


class Authentication(Resource):
    """Authenticate user with their credentials and issue token for them."""

    def on_get(self, req, resp):
        # verify token
        if req.context.auth:
            req.context.auth.verify(req, resp)
        else:
            resp.status = HTTP_SERVICE_UNAVAILABLE

    def on_post(self, req, resp):
        # acquire token
        if req.context.auth:
            req.context.auth.acquire(req, resp)
        else:
            resp.status = HTTP_SERVICE_UNAVAILABLE

    def on_patch(self, req, resp):
        # refresh token
        if req.context.auth:
            req.context.auth.refresh(req, resp)
        else:
            resp.status = HTTP_SERVICE_UNAVAILABLE

    def on_delete(self, req, resp):
        # revoke token
        if req.context.auth:
            req.context.auth.revoke(req, resp)
        else:
            resp.status = HTTP_SERVICE_UNAVAILABLE
