"""Middlewares setup."""

from muria.middleware.require_https import RequireHTTPS
from muria.middleware.auth import AuthMiddleware
from muria.middleware.cors import CORS


class Middlewares():

    def __init__(self, config, **kwargs):
        self.common_middlewares = []
        self.security_middlewares = []

        auth_middleware = AuthMiddleware(
            config.tokenizer,
            exempt_routes=[
                "/v1/ping",
                "/v1/auth",
                "/v1/auth/refresh"
            ],
            exempt_methods=[
                "HEAD",
                "OPTIONS"
            ]
        )

        cors = CORS(
            log_level=config.getint("cors", "log_level"),
            # false means disallow any random host to connect
            allow_all_origins=config.getboolean(
                "cors", "allow_all_origins"
            ),
            allow_origins_list=config.getlist("cors", "allow_origins_list"),
            # allow all methods incl. custom ones are allowed via CORS requests
            allow_all_methods=config.getboolean(
                "cors", "allow_all_methods"
            ),
            allow_methods_list=config.getlist("cors", "allow_methods_list"),
            # for preflight response
            allow_all_headers=config.getboolean(
                "cors", "allow_all_headers"
            ),
            allow_headers_list=config.getlist("cors", "allow_headers_list"),
            allow_credentials_all_origins=config.getboolean(
                "cors", "allow_credentials_all_origins"
            ),
            allow_credentials_origins_list=config.getlist(
                "cors", "allow_credentials_origins_list"
            ),
            max_age=config.getint("cors", "max_age"),
        )

        self.security_middlewares.append(RequireHTTPS())
        self.security_middlewares.append(auth_middleware)
        self.security_middlewares.append(cors.middleware)

        self.middleware_list = self.common_middlewares + \
            self.security_middlewares

    def __call__(self):
        return self.middleware_list
