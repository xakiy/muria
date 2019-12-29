# -*- coding: utf-8 -*-

from .token import BaseToken


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

    def __init__(self, token, exempt_routes=None, exempt_methods=None):
        self.token = token
        if not isinstance(token, BaseToken):
            raise ValueError(
                'Invalid authentication token {0}. Must inherit '
                '`muria.middleware.auth.token.BaseToken`'.format(token)
            )
        self.exempt_routes = exempt_routes or []
        self.exempt_methods = exempt_methods or ['OPTIONS']

    def _get_auth_settings(self, req, resource):
        auth_settings = getattr(resource, 'auth', {})
        auth_settings['exempt_routes'] = self.exempt_routes
        if auth_settings.get('auth_disabled'):
            auth_settings['exempt_routes'].append(req.uri_template)

        for key in ('exempt_methods', 'token'):
            auth_settings[key] = auth_settings.get(key) or getattr(self, key)

        return auth_settings

    def process_resource(self, req, resp, resource, *args, **kwargs):
        auth_setting = self._get_auth_settings(req, resource)
        if (req.uri_template in auth_setting['exempt_routes'] or
                req.method in auth_setting['exempt_methods']):
            return
        token = auth_setting['token']
        req.context.user = token.unload(token.parse_token_header(req))
