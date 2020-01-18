import logging as _logging
from .json import json
from .config import Configuration


def logging(name='Muria_Logging', level=20):
    logger = _logging.getLogger(name)
    logger.setLevel(level)
    logger.propogate = False
    if not logger.handlers:
        handler = _logging.StreamHandler()
        logger.addHandler(handler)
    return logger


__all__ = [
    json,
    logging,
    Configuration
]
