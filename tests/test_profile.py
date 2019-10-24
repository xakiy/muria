"""Profile Resource Test."""

import uuid
import pytest
from pony.orm import db_session
from muria.init import config
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
        query = "id=%s" % self.profile.id[:-2] + generate_chars(2)
        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            query_string=query
        )

        # should get NOT_FOUND
        assert resp.status == HTTP_NOT_FOUND

        # with non-existent uuid
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
        query = "id=%s" % self.profile.id

        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            query_string=query
        )

        # should be OK and match
        assert resp.status == HTTP_OK
        assert resp.json == self.profile.unload()

    @db_session
    def test_edit_profile(self, client, request):

        bio = {
            "id": "7b8bccaa-5f6f-4ac0-a469-432799c12549",
            "nama": "Rijalul Ghad",
            "jinshi": "l",
            "tempat_lahir": "Makasar",
            "tanggal_lahir": "1983-01-28",
            "tanggal_masuk": "2019-08-12",
        }

        assert bio == self.profile.unload()

        valid_id = bio["id"]

        # with invalid bio id
        bio['id'] = bio['id'][:-2] + generate_chars(2)

        payload = dumpAsJSON(bio)

        resp = client.simulate_patch(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            body=payload
        )

        # should return not found
        assert resp.status == HTTP_NOT_FOUND

        valid_jinshi = bio["jinshi"]
        # with invalid jinshi
        bio['id'] = valid_id
        bio['jinshi'] = 'x'

        payload = dumpAsJSON(bio)

        resp = client.simulate_patch(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            body=payload
        )

        # should return unprocessable
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY

        # with invalid date
        bio['jinshi'] = valid_jinshi
        bio['tanggal_masuk'] = "10-31-2019"

        payload = dumpAsJSON(bio)

        resp = client.simulate_patch(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            body=payload
        )

        # should return unprocessable
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY

        # with valid bio id
        bio = self.profile.unload()

        payload = dumpAsJSON(bio)

        resp = client.simulate_patch(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            body=payload
        )

        # should return OK
        assert resp.status == HTTP_OK

        # patch with overloaded data
        bio['foo'] = 'bar'

        payload = dumpAsJSON(bio)

        resp = client.simulate_patch(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            body=payload
        )

        # should return OK
        assert resp.status == HTTP_OK
