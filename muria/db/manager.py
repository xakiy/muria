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


def setup_database(config):
    connection = Database()
    define_entities(connection)
    # connection is imported from model
    params = dict()
    params.update({"provider": config.get("db_engine")})

    # MySQL and PostgreSQL
    if params["provider"] in ("mysql", "postgres"):
        params.update(
            {
                "host": config.get("db_host"),
                "user": config.get("db_user")
            }
        )
        # mysql uses 'passwd' keyword argument instead of 'password'
        if params["provider"] == "mysql":
            params.update(
                {"passwd": config.get("db_password"),
                 "db": config.get("db_name")}
            )
        else:
            params.update(
                {"password": config.get("db_password"),
                 "dbname": config.get("db_name")}
            )
        # for postgres complete list arguments consult to
        # https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS
        if params["provider"] == "postgres":
            if config.get("db_sslmode"):
                params.update(
                    {"sslmode": config.get("db_sslmode")}
                )
            if config.get("db_connect_timeout"):
                params.update(
                    {"connect_timeout": config.get("db_connect_timeout")}
                )
        # use socket if available prior to TCP connection
        if config.get("db_socket"):
            params.update(
                {"unix_socket": config.get("db_socket")}
            )
        else:
            params.update({"port": config.getint("db_port")})
    # SQLite
    elif params["provider"] == "sqlite":
        params.update({"filename": config.get("db_filename")})
        if params["filename"] != ":memory:":
            params.update(
                {"create_db": config.getboolean("db_create_database")}
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

    try:
        verbose = config.getboolean("api_debug") and \
            config.getboolean("db_verbose")
        sql_debug(verbose)
        connection.bind(**params)
        print("main binding")
        print(params)
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

        return connection
    except Exception as err:
        raise err
