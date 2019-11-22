"""Account Resource Test."""

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
    HTTP_UNPROCESSABLE_ENTITY
)


@pytest.fixture(scope="class")
def url(request):
    request.cls.url = "/v1/accounts"


@pytest.fixture(scope="class")
def another_account(request):
    account = {
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
    request.cls.another_account = account


@pytest.mark.usefixtures("client", "url", "properties", "another_account")
class TestAccounts():

    @db_session
    def test_post_account_with_valid_data(self, client, request):
        # post new account
        resp = client.simulate_post(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            json=self.another_account
        )
        # should be CREATED
        assert resp.status == HTTP_CREATED
        assert resp.json.get('username') == self.another_account['username']

        # try re-post it
        resp = client.simulate_post(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            json=self.another_account
        )
        # should be CONFLICT
        assert resp.status == HTTP_CONFLICT

    @db_session
    def test_get_account_with_search(self, client, request):

        username = uri.encode_value(self.another_account['username'])

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
    def test_get_account_without_search(self, client, request):

        # no search
        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme
        )

        # should get OK
        assert resp.status == HTTP_OK
        assert resp.json.get('count') > 0


@pytest.mark.usefixtures("client", "url", "properties", "another_account")
class TestAccountDetail():

    def test_get_account_with_invalid_uuid(self, client, request):
        # with invalid uuid
        resp = client.simulate_get(
            path=self.url + '/%s' % self.user.id[:-2] + generate_chars(2),
            headers=self.headers,
            protocol=self.scheme
        )
        # should get NOT_FOUND
        assert resp.status == HTTP_NOT_FOUND

    def test_get_account_with_random_uuid(self, client, request):
        # with random uuid
        resp = client.simulate_get(
            path=self.url + '/%s' % str(uuid.uuid4()),
            headers=self.headers,
            protocol=self.scheme
        )

        # should get NOT_FOUND
        assert resp.status == HTTP_NOT_FOUND

    def test_get_account_with_correct_uuid(self, client, request):
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
    def test_patch_account_with_random_uuid(self, client, request):
        # replace id with random uuid
        resp = client.simulate_patch(
            path=self.url + '/%s' % str(uuid.uuid4()),
            headers=self.headers,
            protocol=self.scheme
        )

        # should return not found
        assert resp.status == HTTP_NOT_FOUND

    @db_session
    def test_patch_account_with_invalid_jinshi(self, client, request):
        account = self.user.unload()

        # replace jinshi with invalid one
        account['jinshi'] = 'x'

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=account
        )

        # should return unprocessable
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY
        assert resp.json.get('description').get('error').get('jinshi') \
            is not None

    @db_session
    def test_patch_account_with_invalid_date(self, client, request):

        account = self.user.unload()

        # replace date with invalid one
        account['tanggal_masuk'] = "10-31-2019"

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=account
        )
        # assert resp.json.get('description') == ''
        # should return unprocessable
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY
        assert resp.json.get('description').get('error').get('tanggal_masuk') \
            is not None

    @db_session
    def test_patch_account_with_additional_data(self, client, request):
        account = self.user.unload()
        # patch with additional unknown field
        account['foo'] = 'bar'

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=account
        )

        # should be ignored and return OK
        assert resp.status == HTTP_OK

    @db_session
    def test_patch_account_with_valid_modified_data(self, client, request):
        account = self.user.unload()

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
        account.update(edited)

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=account
        )

        # should be OK
        assert resp.status == HTTP_OK
        assert resp.json == account

    @db_session
    def test_patch_account_with_original_data(self, client, request):

        account = self.user.unload()

        resp = client.simulate_patch(
            path=self.url + '/%s' % self.user.id,
            headers=self.headers,
            protocol=self.scheme,
            json=account
        )

        # should return OK
        assert resp.status == HTTP_OK

    @db_session
    def test_delete_account_with_correct_uuid(self, client, request):

        # before we delete an account we need he's uid
        username = uri.encode_value(self.another_account['username'])
        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            params={"search": username}
        )

        # should get OK
        assert resp.status == HTTP_OK
        # get the uid
        uid = resp.json.get('accounts')[0].get('id')
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
