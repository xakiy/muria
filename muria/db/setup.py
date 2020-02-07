"""Preparing database setups."""

import sys
from pony.orm import (
    Database,
    db_session,
    flush,
    sql_debug
)
from pony.orm.dbapiprovider import OperationalError
from muria.db.model import define_entities
tables = []  # no preload data


def initiate(config):
    connection = Database()
    define_entities(connection)
    params = dict()
    params.update({"provider": config.get("db_engine")})

    # MySQL and PostgreSQL
    if params["provider"] in ("mysql", "postgres"):
        params.update(
            {
                "user": config.get("db_user", ""),
                "password": config.get("db_password", "")
            }
        )
        if config.get("db_connect_timeout"):
            params.update(
                {"connect_timeout": config.getint("db_connect_timeout", 10)}
            )
        # mysql uses 'passwd' keyword argument instead of 'password'
        if params["provider"] == "mysql":
            params.update(
                {
                    "db": config.get("db_name"),
                    "charset": config.get("db_encoding", "utf8mb4")
                }
            )
        else:
            params.update(
                {"dbname": config.get("db_name")}
            )
        # for postgres complete list arguments consult to
        # https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS
        if params["provider"] == "postgres":
            if config.get("db_sslmode"):
                params.update(
                    {"sslmode": config.get("db_sslmode")}
                )
    # SQLite
    elif params["provider"] == "sqlite":
        params.update({"filename": config.get("db_filename")})
        if params["filename"] != ":memory:":
            params.update(
                {"create_db": config.getboolean("db_create_database", True)}
            )
    # Oracle
    elif params["provider"] == "oracle":
        params.update(
            {
                "user": config.get("db_user", ""),
                "password": config.get("db_password", ""),
                "dsn": config.get("db_dsn"),
            }
        )
    # make the database scream
    if config.getboolean("api_debug"):
        sql_debug(config.getboolean("db_verbose", False))

    if params["provider"] in ("mysql", "postgres"):
        # use socket if available prior to TCP connection
        if config.get("db_socket"):
            # postgres socket peer connection is not supported
            # if params["provider"] == "postgres" and config.get("db_socket"):
            #     params.update(
            #         {"host": config.get("db_socket")}
            #     )
            if params["provider"] == "mysql":
                params.update(
                    {"unix_socket": config.get("db_socket")}
                )
                try:
                    return _connect(config, connection, params)
                except Exception as err:
                    params.pop("unix_socket")
                    if config.getboolean("api_debug"):
                        raise err

        if config.get("db_host"):
            params.update({"host": config.get("db_host", "localhost")})
        if config.get("db_port"):
            params.update({"port": config.getint("db_port")})
        return _connect(config, connection, params)
    else:
        return _connect(config, connection, params)


def _connect(config, connection, params):
    try:
        # establish connection
        connection.bind(**params)
        # map tables to entities
        connection.generate_mapping(
            create_tables=config.getboolean("db_create_tables")
        )
        _preload_data()
        return connection
    except OperationalError as err:
        raise err


@db_session
def _preload_data():
    # populate preload data if not exist
    if tables is not []:
        for table in tables:
            for row in table['data']:
                model = getattr(sys.modules[__name__], table['model'])
                if not model.exists(**row):
                    model(**row)
        flush()
