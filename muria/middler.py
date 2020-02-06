"""Middlewares setup."""

from muria.middleware.require_https import RequireHTTPS
from muria.middleware.auth import Auth
from muria.middleware.cors import CORS
from muria.util import cache_factory


class Middlewares():

    def __init__(self, config, **kwargs):
        self.middlewares = []

        auth = Auth(
            route_basepath=config.get("api_version"),
            route_path=config.get("api_auth_path", "auth"),
            secret_key=config.get("jwt_secret_key"),
            algorithm=config.get("jwt_algorithm"),
            jwt_header_prefix=config.get("jwt_header_prefix"),
            jwt_refresh_header_prefix=config.get("jwt_refresh_header_prefix"),
            leeway=config.getint("jwt_leeway"),
            jwt_token_exp=config.getint("jwt_token_exp"),
            jwt_refresh_exp=config.getint("jwt_refresh_exp"),
            audience=config.get("jwt_audience"),
            issuer=config.get("jwt_issuer"),
            exempt_routes=[
                "/v1/ping"
            ],
            exempt_methods=[
                "HEAD",
                "OPTIONS"
            ],
            cache=cache_factory(provider=config.get("cache_provider"),
                                host=config.get("cache_host"),
                                port=config.get("cache_port"),
                                prefix="auth_middleware"),
        )

        cors_debug = config.getint("cors_log_level") \
            if config.getboolean("api_debug") else 30
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
        # Order is matter here
        self.middlewares.append(RequireHTTPS())
        self.middlewares.append(cors.middleware)
        self.middlewares.append(auth.middleware)

    def __call__(self):
        return self.middlewares
