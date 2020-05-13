import logging as _logging
from .json import json, json_dumper, json_loader
from .config import Configuration
from .cache import cache_factory
from .misc import generate_chars, is_uuid, get_timestamp


def logging(name='Muria_Logging', level=20):
    logger = _logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    if not logger.handlers:
        handler = _logging.StreamHandler()
        logger.addHandler(handler)
    return logger


__all__ = [
    json,
    json_dumper,
    json_loader,
    cache_factory,
    logging,
    Configuration,
    generate_chars,
    is_uuid,
    get_timestamp
]
