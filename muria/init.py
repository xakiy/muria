"""Bootstraping stuff."""

from muria.util.setting import Parser
from muria.db.manager import setup_database
from muria.util.logger import Logger
from muria.util.auth import Authentication
from falcon_oauth.provider.oauth2 import OAuthProvider

# MURIA_SETUP merupakan env yang menunjuk ke berkas
# konfigurasi produksi atau pengembangan.
# seperti: export MURIA_SETUP=~/config/devel.ini
config = Parser(setup="MURIA_SETUP")

DEBUG = config.getboolean("app", "debug")

logger = Logger(config).getLogger()

setup_database(config)

authentication = Authentication(config)

oauth = OAuthProvider(
    clientgetter=authentication.get_client,
    usergetter=authentication.get_user,
    tokengetter=authentication.get_token,
    tokensetter=authentication.set_token,
    grantgetter=authentication.get_grant,
    grantsetter=authentication.set_grant
)
