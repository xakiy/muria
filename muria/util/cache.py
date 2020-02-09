"""Cache Factory."""

from . import json_dumper, json_loader
from pymemcache.client import base


def json_serializer(key, val):
    if isinstance(val, bytes):
            return val.decode('utf8'), 1
    if isinstance(val, str):
        return val, 1
    return json_dumper(val), 2


def json_deserializer(key, val, flags):
    if flags == 1:
        if isinstance(val, bytes):
            return val.decode('utf8')
        return val
    if flags == 2:
        return json_loader(val)
    raise Exception("Unknown serialization format")


def cache_factory(provider="memcache", host="localhost",
                  port=None, socket=None, prefix=None):

    if provider == "memcached":
        if socket:
            host = socket
        else:
            port = port if port else 11211
            host = (host, port)

        return base.Client(
            server=host,
            serializer=json_serializer,
            deserializer=json_deserializer, key_prefix=prefix)
