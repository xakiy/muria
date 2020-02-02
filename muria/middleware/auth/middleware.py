# -*- coding: utf-8 -*-

from .token import Tacen, Jwt
from muria.db import User, JwtToken
from muria.db.schema import Credentials
from datetime import datetime
from os import urandom
from pony.orm import (
    db_session
)
from falcon import (
    HTTP_OK,
    HTTPBadRequest,
    HTTPUnprocessableEntity,
    HTTPUnauthorized,
    HTTP_RESET_CONTENT
)


class AuthMiddleware(object):

    """
    Auth middleware that uses given authentication token, and some
    optional configuration to authenticate requests. After initializing the
    authentication token globally you can override the token as well as
    other configuration for a particular resource by setting the `auth` attribute
    on it to an instance of this class.

    The authentication token must return an authenticated user which is then
    set as `request.context.user` to be used further down by resources otherwise
    an `falcon.HTTPUnauthorized` exception is raised.

    Args:
        token(:class:`falcon_auth.tokens.AuthBackend`, required): Specifies the auth
            token to be used to authenticate requests

        exempt_routes(list, optional): A list of paths to be excluded while performing
            authentication. Default is ``None``

        exempt_methods(list, optional): A list of paths to be excluded while performing
            authentication. Default is ``['OPTIONS']``

    """

    def __init__(self, auth):
        self.auth = auth

    def _get_auth_settings(self, req, resource):
        settings = getattr(resource, 'auth', {})
        settings['exempt_routes'] = self.auth.exempt_routes
        settings['exempt_methods'] = settings.get('exempt_methods') or \
            self.auth.exempt_methods
        if settings.get('auth_disabled'):
            settings['exempt_routes'].append(req.uri_template)
        return settings

    def process_request(self, req, resp):
        # auth path with truthy parameter
        if req.path == self.auth.path:
            if req.get_param_as_bool('acquire'):
                self.auth.acquire(req, resp)
            elif req.get_param_as_bool('verify'):
                self.auth.verify(req, resp)
            elif req.get_param_as_bool('refresh'):
                self.auth.refresh(req, resp)
            elif req.get_param_as_bool('revoke'):
                self.auth.revoke(req, resp)

    def process_resource(self, req, resp, resource, params):
        auth_setting = self._get_auth_settings(req, resource)
        if (req.uri_template in auth_setting['exempt_routes'] or
                req.method in auth_setting['exempt_methods']):
            return

        token = self.auth.tokenizer.parse_token_header(req)
        # TODO:
        # cache revocation list should check for revoked token
        # if token in cache.getRevocationList:
        #   return
        # TODO:
        # user_id verification is probably needed here
        # or some decryption using fernet
        payload = self.auth.tokenizer.unload(token)
        if payload.get("id"):
            req.context.user = payload
