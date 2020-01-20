"""Middlewares setup."""

from muria.middleware.require_https import RequireHTTPS
from muria.middleware.auth import AuthMiddleware
from muria.middleware.cors import CORS
from muria.middleware.auth import JwtToken


class Middlewares():

    def __init__(self, config, **kwargs):
        self.common_middlewares = []
        self.security_middlewares = []

        # jwt instance
        jwt_token = JwtToken(
            unloader=lambda payload: payload.get("data"),
            secret_key=config.get("jwt_secret_key"),
            algorithm=config.get("jwt_algorithm"),
            token_header_prefix=config.get("jwt_header_prefix"),
            leeway=config.getint("jwt_leeway"),
            expiration_delta=config.getint("jwt_token_exp"),
            audience=config.get("jwt_audience"),
            issuer=config.get("jwt_issuer")
        )

        auth_middleware = AuthMiddleware(
            jwt_token,
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

        cors_debug = config.getint("cors_log_level") if config.getboolean("api_debug") else 30
        cors = CORS(
            log_level=cors_debug,
            # false means disallow any random host to connect
            allow_all_origins=config.getboolean("cors_allow_all_origins"),
            allow_origins_list=config.getlist("cors_allow_origins_list"),
            # allow all methods incl. custom ones are allowed via CORS requests
            allow_all_methods=config.getboolean("cors_allow_all_methods"),
            allow_methods_list=config.getlist("cors_allow_methods_list"),
            # for preflight response
            allow_all_headers=config.getboolean("cors_allow_all_headers"),
            allow_headers_list=config.getlist("cors_allow_headers_list"),
            allow_credentials_all_origins=config.getboolean(
                "cors_allow_credentials_all_origins"
            ),
            allow_credentials_origins_list=config.getlist(
                "cors_allow_credentials_origins_list"
            ),
            max_age=config.getint("cors_max_age"),
        )

        self.security_middlewares.append(RequireHTTPS())
        self.security_middlewares.append(auth_middleware)
        self.security_middlewares.append(cors.middleware)

        self.middleware_list = self.common_middlewares + \
            self.security_middlewares

    def __call__(self):
        return self.middleware_list
