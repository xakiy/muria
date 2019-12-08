"""Bootstraping stuff."""

from muria.util.setting import Parser
from muria.db.manager import setup_database
from muria.util.logger import Logger
from muria.util.auth import Authentication


# MURIA_SETUP merupakan env yang menunjuk ke berkas
# konfigurasi produksi atau pengembangan.
# seperti: export MURIA_SETUP=~/config/devel.ini
config = Parser(setup="MURIA_SETUP")

DEBUG = config.getboolean("app", "debug")

logger = Logger(config).getLogger()

setup_database(config)

authentication = Authentication(config)
