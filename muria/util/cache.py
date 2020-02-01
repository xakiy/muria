"""Cache Factory."""

from . import json_dumper, json_loader
from pymemcache.client import base


def json_serializer(key, val):
    if isinstance(val, str):
        return val, 1
    return json_dumper(val), 2


def json_deserializer(key, val, flags):
    if flags == 1:
        return val
    if flags == 2:
        return json_loader(val)
    raise Exception("Unknown serialization format")


def cache_factory(provider="memcache", host="localhost",
                  port=None, prefix=None):

    if provider == "memcache":
        return base.Client(
            (host, port),
            serializer=json_serializer,
            deserializer=json_deserializer, key_prefix=prefix)
