"""Bootstraping stuff."""

from muria.util import Configuration
from muria.db.manager import setup_database
from muria.util import logging
from muria.middleware.auth import JwtToken

# MURIA_CONFIG merujuk ke berkas konfigurasi
# seperti: export MURIA_CONFIG=~/config/devel.ini
config = Configuration(filename="MURIA_CONFIG", mode="MURIA_MODE")

DEBUG = config.getboolean("api_debug")

logger = logging(name=config.get('api_log_name'),
                 level=config.getint('api_log_level'))

setup_database(config)

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

config.tokenizer = jwt_token
