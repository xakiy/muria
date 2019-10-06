"""Bootstraping stuff."""

from muria.lib.config import Parser
from muria.db.setup import setup_database

from muria.lib.user import UserAuthentication
from muria.lib.logger import Logger


# MURIA_SETUP merupakan env yang menunjuk ke berkas
# konfigurasi produksi atau pengembangan.
# seperti: export MURIA_SETUP=~/config/devel.ini
config = Parser(setup="MURIA_SETUP")

DEBUG = config.getboolean("app", "debug")

logger = Logger(config).getLogger()

setup_database(config)

user_authentication = UserAuthentication(config)
