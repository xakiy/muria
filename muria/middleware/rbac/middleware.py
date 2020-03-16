import falcon

from pony.orm import db_session
from muria.db import User
from .config import PolicyConfig
from .manager import PolicyManager


class RBAC:
    # NOTE:
    # It requires jwt_checker middleware declared before itself
    # in order to work.

    # Added check_jwt if roles are passed within jwt claims
    # as an alternative if we don't want to pass X-Roles
    # inside every request header.
    def __init__(self, config_dict):
        self.config = PolicyConfig(config_dict)
        self.manager = PolicyManager(self.config)

    @db_session
    def process_resource(self, req, resp, resource, params):

        # noop if auth resource is requested
        if req.context.auth:
            return
        elif req.context.user:
            route = req.uri_template

            # if self.check_jwt and isinstance(params, dict):
            #     claims = params.get("jwt_claims")
            #     roles_header = (
            #         isinstance(claims, dict) and claims.get("roles") or "@unknown"
            #     )
            # else:
            #     roles_header = req.get_header("X-Roles", default="@unknown")

            # 1. Query user group
            user = User.get(id=req.context.user.get("id"))
            provided_roles = user.get_responsibilities()

            route_policy = self.manager.policies.get(route, {})
            method_policy = route_policy.get(req.method.upper(), [])

            has_role = self.manager.check_roles(provided_roles, method_policy)

            if not has_role:
                raise falcon.HTTPForbidden(
                    description="Access to this resource has been restricted"
                )
