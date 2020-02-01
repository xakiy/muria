"""
    Muria
    Falcon boilerplate for API development.

    Copyright: (c) 2020 by Ahmad Ghulam Zakiy.
    License: MIT License, see LICENSE for more details.
"""
from .version import name, version, author
from muria.util import Configuration
from muria.util import logging
import os


# MURIA_CONFIG merujuk ke berkas konfigurasi
# seperti: export MURIA_CONFIG=~/config/devel.ini
ini_file = str(os.environ.get("MURIA_CONFIG"))
ini_section = str(os.environ.get("MURIA_MODE"))

__app__ = name
__version__ = version
__author__ = author
__license__ = 'MIT License'

config = Configuration(env_ini=ini_file, env_mode=ini_section)

API_NAME = config.get("api_name")
API_MODE = config.get("api_version")
DEBUG = config.getboolean("api_debug")

logger = logging(name=config.get('api_log_name'),
                 level=config.getint('api_log_level'))

print("------------------------------------------------------------")
print("# API Name: %s, v%s" % (API_NAME, API_MODE))
print("# API Mode: %s" % config.get('api_mode'))
print("# Engine: %s Ver. %s" % (name, version))
print("# Copyright %s" % author)
print("------------------------------------------------------------")
print("# DEBUG MODE IS: %s" % 'ON' if DEBUG else 'OFF')
print("------------------------------------------------------------")
