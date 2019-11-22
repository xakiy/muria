"""Profile Resource Test."""

import uuid
import pytest
from pony.orm import db_session
from muria.util.misc import generate_chars
from falcon import (
    uri,
    HTTP_OK,
    HTTP_CREATED,
    HTTP_CONFLICT,
    HTTP_NOT_FOUND,
    HTTP_UNPROCESSABLE_ENTITY
)


@pytest.fixture(scope="class")
def url(request):
    request.cls.url = "/v1/profile"


@pytest.mark.usefixtures("client", "url", "properties")
class TestProfiles():

    @db_session
    def test_post_profile_with_valid_data(self, client, request):

        profile = {
            "nama": "Rijalul Akhor",
            "jinshi": "l",
            "tempat_lahir": "Minangkabau",
            "tanggal_lahir": "1985-04-11",
            "username": "rijalul.akhor",
            "situs": "https://anothersite.com",
            "email": "rijalul.akhor@gmail.com",
            "password": 'anothersecret',
            "suspended": False,
        }

        # no query_string
        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            params={"search": uri.encode_value(profile['username'])},
        )

        if resp.status == HTTP_OK:

            resp = client.simulate_post(
                path=self.url,
                headers=self.headers,
                protocol=self.scheme,
                json=profile
            )
            # should be CONFLICT
            assert resp.status == HTTP_CONFLICT
        else:
            resp = client.simulate_post(
                path=self.url,
                headers=self.headers,
                protocol=self.scheme,
                json=profile
            )
            # should be CREATED
            assert resp.status == HTTP_CREATED
            assert resp.json.get('username') == profile['username']

    @db_session
    def test_get_profile_with_search(self, client, request):

        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            params={"search": uri.encode_value('rijalul')},
        )

        # should get OK
        assert resp.status == HTTP_OK
        assert resp.json.get('count') > 0

    @db_session
    def test_get_profile_without_search(self, client, request):

        # no search
        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme
        )

        # should get OK
        assert resp.status == HTTP_OK
        assert resp.json.get('count') > 0


@pytest.mark.usefixtures("client", "url", "properties")
class TestProfileDetail():

    def test_get_profile_with_invalid_uuid(self, client, request):
        # with invalid uuid
        resp = client.simulate_get(
            path=self.url + '/%s' % self.user.id[:-2] + generate_chars(2),
            headers=self.headers,
            protocol=self.scheme
        )
        # should get NOT_FOUND
        assert resp.status == HTTP_NOT_FOUND

    def test_get_profile_with_random_uuid(self, client, request):
        # with random uuid
        resp = client.simulate_get(
            path=self.url + '/%s' % str(uuid.uuid4()),
            headers=self.headers,
            protocol=self.scheme
        )

        # should get NOT_FOUND
        assert resp.status == HTTP_NOT_FOUND

    def test_get_profile_with_correct_uuid(self, client, request):
        # with correct uuid
        resp = client.simulate_get(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme
        )

        # should be OK and match
        assert resp.status == HTTP_OK
        assert resp.json == self.user.unload()

    @db_session
    def test_patch_profile_with_random_uuid(self, client, request):
        # replace id with random uuid
        resp = client.simulate_patch(
            path=self.url + '/%s' % str(uuid.uuid4()),
            headers=self.headers,
            protocol=self.scheme
        )

        # should return not found
        assert resp.status == HTTP_NOT_FOUND

    @db_session
    def test_patch_profile_with_invalid_jinshi(self, client, request):
        profile = self.user.unload()

        # replace jinshi with invalid one
        profile['jinshi'] = 'x'

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=profile
        )

        # should return unprocessable
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY
        assert resp.json.get('description').get('error').get('jinshi') \
            is not None

    @db_session
    def test_patch_profile_with_invalid_date(self, client, request):

        profile = self.user.unload()

        # replace date with invalid one
        profile['tanggal_masuk'] = "10-31-2019"

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=profile
        )
        # assert resp.json.get('description') == ''
        # should return unprocessable
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY
        assert resp.json.get('description').get('error').get('tanggal_masuk') \
            is not None

    @db_session
    def test_patch_profile_with_additional_data(self, client, request):
        profile = self.user.unload()
        # patch with additional unknown field
        profile['foo'] = 'bar'

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=profile
        )

        # should be ignored and return OK
        assert resp.status == HTTP_OK

    @db_session
    def test_patch_profile_with_valid_modified_data(self, client, request):
        profile = self.user.unload()

        edited = {
            "nama": "Nisa'ul Aan",
            "jinshi": "p",
            "tempat_lahir": "Balikpapan",
            "tanggal_lahir": "1985-11-27",
            "tanggal_masuk": "2019-10-02",
            "username": "nisaul.aan",
            "email": "nisaul.aan@gmail.com"
        }
        # update with edited data
        profile.update(edited)

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=profile
        )

        # should be OK
        assert resp.status == HTTP_OK
        assert resp.json == profile

    @db_session
    def test_patch_profile_with_original_data(self, client, request):

        profile = self.user.unload()

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=profile
        )

        # should return OK
        assert resp.status == HTTP_OK
