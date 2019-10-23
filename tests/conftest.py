"""Fixtures."""

import pytest
from falcon import testing
from muria.init import config
from tests import config_file  # initiating env setup
from muria.wsgi import app
from muria.db.model import Bio, User
from pony.orm import db_session


@pytest.fixture
def client():
    return testing.TestClient(app)


@pytest.fixture(scope="class", autouse=True)
@db_session
def properties(request):

    request.cls.scheme = "https"

    headers = {
        "Host": config.get("security", "issuer"),
        "Origin": config.get("security", "audience"),
    }
    request.cls.headers = headers

    profile_data = {
        "id": "7b8bccaa-5f6f-4ac0-a469-432799c12549",
        "nama": "Rijalul Ghad",
        "jinshi": "l",
        "tempat_lahir": "Makasar",
        "tanggal_lahir": "1983-01-28",
        "tanggal_masuk": "2019-08-12",
    }

    request.cls.profile = Bio.get(id=profile_data["id"]) \
        if Bio.exists(id=profile_data["id"]) else Bio(**profile_data)

    password_string = "supersecret"
    hashed, salt = (
        '0d2f943bf584cc8d2181bb6678c6a8cdd459e43b231720f4a69b735d07e50910',
        '56d7a4c162c754262f90f345ac67c1841c715b3c'
    )

    user_data = {
        "id": "ed05547a-a6be-436f-9f8b-946dee956191",
        "profile": request.cls.profile,
        "username": "rijalul.ghad",
        "email": "rijalul.ghad@gmail.com",
        "password": hashed,
        "salt": salt,
        "suspended": False,
    }

    request.cls.user = User.get(id=user_data["id"]) \
        if User.exists(id=user_data["id"]) else User(**user_data)

    request.cls.password_string = password_string
