#!/env/python

from muria.db import JwtToken
from datetime import datetime
from pony.orm import db_session
import logging

# Invoke this script via shell or bash script
# then you can call it via cron.
# Make sure to activate MURIA virtualenv before
# invoking this script, since all project dependencies is
# within that virtualenv.
#
# create a script, e.g.:
# #!/bin/sh
# # activate Muria virtualenv
# source /absolute/path/to/muria/virtualenv/bin/activate
# env python /absolute/path/to/this/purge_tokens.py
#
# test it before use!


def now():
    return datetime.utcnow().timestamp()


# deleting all revoked tokens
@db_session
def purge_revoked():
    x = JwtToken.select(lambda x: x.get_expires_at() < now() and
        x.revoked == True).delete(bulk=True)
    logging.info(x)
    print('Purging expired token: %d token(s) purged.' % x)


if __name__ == "__main__":
    purge_revoked()
