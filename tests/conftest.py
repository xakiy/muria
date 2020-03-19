"""Fixtures."""

import pytest
from falcon import testing
from muria import config
from muria.wsgi import app
from muria.db import User, Role
from pony.orm import db_session


@pytest.fixture
def client():
    return testing.TestClient(app)


@pytest.fixture(scope="class", autouse=True)
@db_session
def properties(request):

    request.cls.scheme = "https"

    headers = {
        "Host": config.get("jwt_issuer"),
        "Origin": config.get("jwt_audience"),
    }
    request.cls.headers = headers

    password_string = "supersecret"

    role = Role.get(name="administrator")

    user_data = {
        "id": "ed05547a-a6be-436f-9f8b-946dee956191",
        "nama": "Rijalul Ghad",
        "jinshi": "l",
        "tempat_lahir": "Makasar",
        "tanggal_lahir": "1983-01-28",
        "username": "rijalul.ghad",
        "situs": "https://somesite.com",
        "email": "rijalul.ghad@gmail.com",
        "password": password_string,
        "suspended": False,
        "roles": role,
    }

    request.cls.user = User.get(id=user_data["id"]) \
        if User.exists(id=user_data["id"]) else User(**user_data)

    request.cls.password_string = password_string
