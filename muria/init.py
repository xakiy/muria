"""Bootstraping stuff."""

from muria.util.setting import Parser
from muria.db.manager import setup_database
from muria.util.logger import Logger
from muria.middleware.auth import JwtToken

# MURIA_SETUP merupakan env yang menunjuk ke berkas
# konfigurasi produksi atau pengembangan.
# seperti: export MURIA_SETUP=~/config/devel.ini
config = Parser(setup="MURIA_SETUP")

DEBUG = config.getboolean("app", "debug")

logger = Logger(config).getLogger()

setup_database(config)

jwt_token = JwtToken(
    unloader=lambda payload: payload.get("data"),
    secret_key=config.get("security", "secret_key"),
    algorithm=config.get("security", "algorithm"),
    leeway=0,
    expiration_delta=config.getint("security", "access_token_exp"),
    audience=config.get("security", "audience"),
    issuer=config.get("security", "issuer")
)

config.tokenizer = jwt_token
