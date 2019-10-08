"""Testing Account Resource."""

import uuid
from pony.orm import db_session
from muria.init import config
from muria.lib.misc import generate_chars, dumpAsJSON
from falcon import (
    HTTP_OK,
    HTTP_NOT_FOUND,
    HTTP_UNPROCESSABLE_ENTITY
)


class Profile():
    @db_session
    def test_get_profile(self, client, request):

        url = "/v1/profile"

        # headers updated based on header requirements
        headers = {
            "Content-Type": "application/json",
            "Host": config.get("security", "issuer"),
            "Origin": config.get("security", "audience")
        }

        # no query_string
        resp = client.simulate_get(
            path=url,
            headers=headers,
            protocol=self.protocol
        )

        # should got NOT_FOUND
        assert resp.status == HTTP_NOT_FOUND

        # with invalid uuid
        query = "id=%s" % self.user_profile.id[:-2] + generate_chars(2)
        resp = client.simulate_get(
            path=url,
            headers=headers,
            protocol=self.protocol,
            query_string=query
        )

        # should got NOT_FOUND
        assert resp.status == HTTP_NOT_FOUND

        # with non-existent uuid
        query = "id=%s" % str(uuid.uuid4())
        resp = client.simulate_get(
            path=url,
            headers=headers,
            protocol=self.protocol,
            query_string=query
        )

        # should got NOT_FOUND
        assert resp.status == HTTP_NOT_FOUND

        # with correct uuid
        query = "id=%s" % self.user_profile.id

        resp = client.simulate_get(
            path=url,
            headers=headers,
            protocol=self.protocol,
            query_string=query
        )

        # should be OK and match
        assert resp.status == HTTP_OK
        assert resp.json == self.user_profile.unload()

    @db_session
    def test_edit_profile(self, client, request):

        url = "/v1/profile"

        # headers updated based on header requirements
        headers = {
            "Content-Type": "application/json",
            "Host": config.get("security", "issuer"),
            "Origin": config.get("security", "audience")
        }

        bio = {
            "id": "7b8bccaa-5f6f-4ac0-a469-432799c12549",
            "nama": "Rijalul Ghad",
            "jinshi": "l",
            "tempat_lahir": "Makasar",
            "tanggal_lahir": "1983-01-28",
            "tanggal_masuk": "2019-08-12",
        }

        assert bio == self.user_profile.unload()

        valid_id = bio["id"]

        # with invalid bio id
        bio['id'] = bio['id'][:-2] + generate_chars(2)

        payload = dumpAsJSON(bio)

        resp = client.simulate_patch(
            path=url,
            headers=headers,
            protocol=self.protocol,
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
            path=url,
            headers=headers,
            protocol=self.protocol,
            body=payload
        )

        # should return unprocessable
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY

        # with invalid date
        bio['jinshi'] = valid_jinshi
        bio['tanggal_masuk'] = "10-31-2019"

        payload = dumpAsJSON(bio)

        resp = client.simulate_patch(
            path=url,
            headers=headers,
            protocol=self.protocol,
            body=payload
        )

        # should return unprocessable
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY

        # with valid bio id
        bio = self.user_profile.unload()

        payload = dumpAsJSON(bio)

        resp = client.simulate_patch(
            path=url,
            headers=headers,
            protocol=self.protocol,
            body=payload
        )

        # should return OK
        assert resp.status == HTTP_OK

        # patch with overloaded data
        bio['foo'] = 'bar'

        payload = dumpAsJSON(bio)

        resp = client.simulate_patch(
            path=url,
            headers=headers,
            protocol=self.protocol,
            body=payload
        )

        # should return OK
        assert resp.status == HTTP_OK
