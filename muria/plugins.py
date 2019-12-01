from muria.init import config
from muria.middleware.require_https import RequireHTTPS
from muria.middleware.cors import CORS
from falcon_oauth.provider.oauth2 import OAuthProvider
from falcon_oauth.utils import utcnow


common_middlewares = []
security_middlewares = []

cors = CORS(
    log_level=config.getint("cors", "log_level"),
    allow_all_origins=config.getboolean(
        "cors", "allow_all_origins"
    ),  # false means disallow any random host to connect
    allow_origins_list=config.getlist("cors", "allow_origins_list"),
    allow_all_methods=config.getboolean(
        "cors", "allow_all_methods"
    ),  # allow all methods incl. custom ones are allowed via CORS requests
    allow_methods_list=config.getlist("cors", "allow_methods_list"),
    # exposed value sent as response to the Access-Control-Expose-Headers request
    expose_headers_list=config.getlist("cors", "expose_headers_list"),
    allow_all_headers=config.getboolean(
        "cors", "allow_all_headers"
    ),  # for preflight response
    allow_headers_list=config.getlist("cors", "allow_headers_list"),
    allow_credentials_all_origins=config.getboolean(
        "cors", "allow_credentials_all_origins"
    ),
    allow_credentials_origins_list=config.getlist(
        "cors", "allow_credentials_origins_list"
    ),
    max_age=config.getint("cors", "max_age"),
)

security_middlewares.append(RequireHTTPS())
security_middlewares.append(cors.middleware)

middleware_list = common_middlewares  + security_middlewares
