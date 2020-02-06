"""Authentication Resource."""

from muria.common.resource import Resource
from falcon import (
    HTTP_SERVICE_UNAVAILABLE,
    HTTPMissingParam,
    HTTPBadRequest
)


class Authentication(Resource):
    """Authenticate user with their credentials and issue token for them."""

    def on_post(self, req, resp):
        if req.context.auth:
            route = ("acquire", "verify", "refresh", "revoke")
            if req.params and req.params.get("mode"):
                mode = req.params.get("mode")
                if mode in route:
                    responder = getattr(req.context.auth, mode)
                    responder(req, resp)
                else:
                    # no such mode
                    raise HTTPBadRequest(description="No such mode implemented")
            else:
                raise HTTPMissingParam(param_name="mode")
        else:
            resp.status = HTTP_SERVICE_UNAVAILABLE
