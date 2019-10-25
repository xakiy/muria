"""Profile Resource Test."""

import uuid
import pytest
from pony.orm import db_session
from muria.util.misc import generate_chars
from muria.util.json import dumpAsJSON
from falcon import (
    HTTP_OK,
    HTTP_NOT_FOUND,
    HTTP_UNPROCESSABLE_ENTITY
)


@pytest.fixture(scope="class")
def url(request):
    request.cls.url = "/v1/profile"


@pytest.mark.usefixtures("client", "url", "properties")
class TestProfile():
    @db_session
    def test_get_profile(self, client, request):

        # no query_string
        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme
        )

        # should get NOT_FOUND
        assert resp.status == HTTP_NOT_FOUND

        # with invalid uuid
        query = "id=%s" % self.user.id[:-2] + generate_chars(2)
        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            query_string=query
        )

        # should get NOT_FOUND
        assert resp.status == HTTP_NOT_FOUND

        # with random uuid
        query = "id=%s" % str(uuid.uuid4())
        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            query_string=query
        )

        # should get NOT_FOUND
        assert resp.status == HTTP_NOT_FOUND

        # with correct uuid
        query = "id=%s" % self.user.id

        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            query_string=query
        )

        # should be OK and match
        assert resp.status == HTTP_OK
        assert resp.json == self.user.unload()

    @db_session
    def test_edit_profile(self, client, request):

        profile = {
            "id": "ed05547a-a6be-436f-9f8b-946dee956191",
            "nama": "Rijalul Ghad",
            "jinshi": "l",
            "tempat_lahir": "Makasar",
            "tanggal_lahir": "1983-01-28",
            "tanggal_masuk": "2019-08-12",
            "username": "rijalul.ghad",
            "email": "rijalul.ghad@gmail.com"
        }

        # with random uuid
        profile["id"] = "id=%s" % str(uuid.uuid4())

        payload = dumpAsJSON(profile)

        resp = client.simulate_patch(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            body=payload
        )

        # should return not found
        assert resp.status == HTTP_NOT_FOUND

        # with correct uuid
        profile["id"] = self.user.id

        # but with invalid jinshi
        profile['jinshi'] = 'x'

        payload = dumpAsJSON(profile)

        resp = client.simulate_patch(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            body=payload
        )

        # should return unprocessable
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY

        # with invalid date
        profile['jinshi'] = self.user.jinshi
        profile['tanggal_masuk'] = "10-31-2019"

        payload = dumpAsJSON(profile)

        resp = client.simulate_patch(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            body=payload
        )

        # should return unprocessable
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY

        profile['tanggal_masuk'] = self.user.tanggal_masuk

        payload = dumpAsJSON(profile)

        resp = client.simulate_patch(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            body=payload
        )

        # should return OK
        assert resp.status == HTTP_OK

        # patch with additional unknown field
        profile['foo'] = 'bar'

        payload = dumpAsJSON(profile)

        resp = client.simulate_patch(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            body=payload
        )

        # should be ignored and return OK
        assert resp.status == HTTP_OK
