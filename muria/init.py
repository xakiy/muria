"""Bootstraping stuff."""

from muria.util.setting import Parser
from muria.db.manager import setup_database

from muria.util.user import UserAuthentication
from muria.util.logger import Logger


# MURIA_SETUP merupakan env yang menunjuk ke berkas
# konfigurasi produksi atau pengembangan.
# seperti: export MURIA_SETUP=~/config/devel.ini
config = Parser(setup="MURIA_SETUP")

DEBUG = config.getboolean("app", "debug")

logger = Logger(config).getLogger()

setup_database(config)

user_authentication = UserAuthentication(config)
