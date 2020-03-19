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


def get_params(config):
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
        # https://www.postgresql.org/docs/current/libpq-connect.html
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

    if params["provider"] in ("mysql", "postgres"):
        # use socket if available prior to TCP connection
        if config.get("db_socket"):
            # NOTE:
            # postgres socket peer connection is not supported
            if params["provider"] == "mysql":
                params.update(
                    {"unix_socket": config.get("db_socket")}
                )
        if config.get("db_host"):
            params.update({"host": config.get("db_host", "localhost")})
        if config.get("db_port"):
            params.update({"port": config.getint("db_port")})
    return params


def bind(connection, params):
    if params["provider"] == "mysql":
        if params.get("unix_socket"):
            try:
                # try socket first
                connection.bind(**params)
            except Exception:
                params.pop("unix_socket")
        else:
            # otherwise try tcp/ip
            connection.bind(**params)
    else:
        try:
            connection.bind(**params)
        except OperationalError as err:
            raise err
    return connection


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


def connect(config):
    connection = Database()
    define_entities(connection)

    # make the database scream
    if config.getboolean("api_debug"):
        sql_debug(config.getboolean("db_verbose", False))

    # bind database
    params = get_params(config)
    bind(connection, params)

    # TODO:
    # We can make automated migration process here before entity mapping
    # something like below.
    # connection.execute("ALTER TABLE users ADD COLUMN picture VARCHAR(254) NULL DEFAULT ''")
    # connection.commit()

    # map tables to entities
    connection.generate_mapping(create_tables=config.getboolean("db_create_tables", True))
    _preload_data()

    return connection
