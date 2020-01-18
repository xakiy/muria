"""Preparing database setups."""

import sys
from pony.orm import (
    db_session,
    flush,
    sql_debug
)
from pony.orm.dbapiprovider import OperationalError
from muria.db.model import *  # connection included
tables = []  # no preload data


def setup_database(config, conection=connection):
    # connection is imported from model

    params = dict()
    params.update({"provider": config.get("db_engine")})
    # MySQL and PostgreSQL
    if params["provider"] in ("mysql", "postgres"):
        params.update(
            {
                "host": config.get("db_host"),
                "user": config.get("db_user"),
                "db": config.get("db_db"),
            }
        )
        # mysql uses 'passwd' keyword argument instead of 'password'
        if params["provider"] == "mysql":
            params.update({"passwd": config.get("db_password")})
        else:
            params.update(
                {"password": config.get("db_password")}
            )
        # use socket if available prior to TCP connection
        if config.get("db_socket"):
            params.update(
                {"unix_socket": config.get("db_socket")}
            )
        port = config.get("db_port")
        if port is not None and port.isnumeric():
            params.update({"port": int(port)})
    # SQLite
    elif params["provider"] == "sqlite":
        params.update({"filename": config.get("db_filename")})
        if params["filename"] != ":memory:":
            params.update(
                {"create_db": config.getboolean("db_create_db")}
            )
    # Oracle
    elif params["provider"] == "oracle":
        params.update(
            {
                "user": config.get("db_user"),
                "password": config.get("db_password"),
                "dsn": config.get("db_dsn"),
            }
        )

    if params["provider"] in ("mysql", "postgres"):
        options = params.copy()
        # if socket provided try to use it first
        if params.get("unix_socket") is not None:
            try:
                if params.get("port"):
                    params.pop("port")
                connection.bind(**params)
            # otherwise use TCP port
            except OperationalError:
                options.pop("unix_socket")
                connection.bind(**options)
                params = options
    else:
        connection.bind(**params)

    verbose = config.getboolean("api_debug") and \
        config.getboolean("db_verbose")
    sql_debug(verbose)
    connection.generate_mapping(
        create_tables=config.getboolean("db_create_table")
    )

    # populate preload data if not exist
    if tables is not []:
        with db_session:
            for table in tables:
                for row in table['data']:
                    model = getattr(sys.modules[__name__], table['model'])
                    if not model.exists(**row):
                        model(**row)
            flush()
