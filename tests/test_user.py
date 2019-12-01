"""User Resource Test."""

import uuid
import pytest
from pony.orm import db_session
from muria.util.misc import generate_chars
from falcon import (
    uri,
    HTTP_OK,
    HTTP_GONE,
    HTTP_CREATED,
    HTTP_CONFLICT,
    HTTP_NOT_FOUND,
    HTTP_BAD_REQUEST,
    HTTP_UNPROCESSABLE_ENTITY
)


@pytest.fixture(scope="class")
def url(request):
    request.cls.url = "/v1/users"


@pytest.fixture(scope="class")
def another_user(request):
    user = {
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
    request.cls.another_user = user


@pytest.mark.usefixtures("client", "url", "properties", "another_user")
class TestUsers():

    @db_session
    def test_post_user_with_no_payload(self, client):
        # post no payload
        resp = client.simulate_post(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme
        )
        # should be BAD REQUEST
        assert resp.status == HTTP_BAD_REQUEST

    @db_session
    def test_post_user_with_invalid_data(self, client):

        data = self.another_user.copy()

        # tampered the data
        data['username'] = 'unllowed-username'
        # post new user
        resp = client.simulate_post(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            json=data
        )
        # should be UNPROCESSABLE ENTITY
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY

        # tampered the data
        data['username'] = 'un@llowed-username'
        # post new user
        resp = client.simulate_post(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            json=data
        )
        # should be UNPROCESSABLE ENTITY
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY

        # tampered the data
        data['jinshi'] = 'x'
        # post new user
        resp = client.simulate_post(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            json=data
        )
        # should be UNPROCESSABLE ENTITY
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY

    @db_session
    def test_post_user_with_valid_data(self, client):
        # post new user
        resp = client.simulate_post(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            json=self.another_user
        )
        # should be CREATED
        assert resp.status == HTTP_CREATED
        assert resp.json.get('username') == self.another_user['username']

    @db_session
    def test_post_repost_user_with_valid_data(self, client):
        # try re-post it
        resp = client.simulate_post(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            json=self.another_user
        )
        # should be CONFLICT
        assert resp.status == HTTP_CONFLICT

    @db_session
    def test_get_user_with_incorrect_search(self, client):

        username = uri.encode_value('random.name.you.can.imagine')

        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            params={"search": username}
        )

        # should get NOT FOUND
        assert resp.status == HTTP_NOT_FOUND

    @db_session
    def test_get_user_with_correct_search(self, client):

        username = uri.encode_value(self.another_user['username'])

        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            params={"search": username}
        )

        # should get OK
        assert resp.status == HTTP_OK
        assert resp.json.get('count') == 1

    @db_session
    def test_get_user_without_search(self, client):

        # plain get
        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme
        )

        # assuming there were any users already populated in the db
        # this should get OK
        assert resp.status == HTTP_OK
        assert resp.json.get('count') > 0

    @db_session
    def test_get_user_with_valid_pagination(self, client):

        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            params={"index": 1, "count": 1}
        )

        # assuming there were only 2 users already populated in the db
        assert resp.status == HTTP_OK
        assert resp.json.get('count') == 1

    @db_session
    def test_get_user_with_out_of_range_pagination(self, client):

        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            params={"index": 10, "count": 1}
        )
        assert resp.status == HTTP_NOT_FOUND


@pytest.mark.usefixtures("client", "url", "properties", "another_user")
class TestUserDetail():

    def test_get_user_with_invalid_uuid(self, client):
        # with invalid uuid
        resp = client.simulate_get(
            path=self.url + '/%s' % self.user.id[:-2] + generate_chars(2),
            headers=self.headers,
            protocol=self.scheme
        )
        # should get NOT_FOUND
        assert resp.status == HTTP_NOT_FOUND

    def test_get_user_with_random_uuid(self, client):
        # with random uuid
        resp = client.simulate_get(
            path=self.url + '/%s' % str(uuid.uuid4()),
            headers=self.headers,
            protocol=self.scheme
        )

        # should get NOT_FOUND
        assert resp.status == HTTP_NOT_FOUND

    def test_get_user_with_correct_uuid(self, client):
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
    def test_patch_user_with_random_uuid(self, client):
        # replace id with random uuid
        resp = client.simulate_patch(
            path=self.url + '/%s' % str(uuid.uuid4()),
            headers=self.headers,
            protocol=self.scheme
        )

        # should return not found
        assert resp.status == HTTP_NOT_FOUND

    @db_session
    def test_patch_user_with_invalid_jinshi(self, client):
        user = self.user.unload()

        # replace jinshi with invalid one
        user['jinshi'] = 'x'

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=user
        )

        # should return unprocessable
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY
        assert resp.json.get('description').get('error').get('jinshi') \
            is not None

    @db_session
    def test_patch_user_with_invalid_date(self, client):

        user = self.user.unload()

        # replace date with invalid one
        user['tanggal_masuk'] = "10-31-2019"

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=user
        )
        # assert resp.json.get('description') == ''
        # should return unprocessable
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY
        assert resp.json.get('description').get('error').get('tanggal_masuk') \
            is not None

    @db_session
    def test_patch_user_with_additional_data(self, client):
        user = self.user.unload()
        # patch with additional unknown field
        user['foo'] = 'bar'

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=user
        )

        # should be ignored and return OK
        assert resp.status == HTTP_OK

    @db_session
    def test_patch_user_with_valid_modified_data(self, client):
        user = self.user.unload()

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
        user.update(edited)

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=user
        )

        # should be OK
        assert resp.status == HTTP_OK
        assert resp.json == user

    @db_session
    def test_patch_user_with_original_data(self, client):

        user = self.user.unload()

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=user
        )

        # should return OK
        assert resp.status == HTTP_OK

    @db_session
    def test_delete_user_with_correct_uuid(self, client):

        # before we delete an user we need he's uid
        username = uri.encode_value(self.another_user['username'])
        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            params={"search": username}
        )

        # should get OK
        assert resp.status == HTTP_OK
        # get the uid
        uid = resp.json.get('users')[0].get('id')
        # assert resp.json == ''

        resp = client.simulate_delete(
            path=self.url + '/%s' % uid,
            headers=self.headers,
            protocol=self.scheme
        )

        # should return GONE
        assert resp.status == HTTP_GONE

        # try re-delete it
        resp = client.simulate_delete(
            path=self.url + '/%s' % uid,
            headers=self.headers,
            protocol=self.scheme
        )

        # should return NOT FOUND
        assert resp.status == HTTP_NOT_FOUND
