"""Authentication Test."""

import pytest
import base64
from muria.init import DEBUG, user_authentication
# from muria.util.json import dumpAsJSON
from urllib import parse
from muria.util.misc import generate_chars
from falcon import (
    HTTP_BAD_REQUEST,
    HTTP_UNPROCESSABLE_ENTITY,
    HTTP_UNAUTHORIZED,
    HTTP_OK
)


@pytest.fixture(scope="class")
def url(request):
    request.cls.url = "/v1/auth"


@pytest.mark.usefixtures("client", "url", "properties")
class TestAuth:

    def test_get_auth(self, client):

        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme
        )

        assert resp.status == HTTP_OK
        assert resp.headers.get('www-authenticate') == 'Bearer'
        if DEBUG:
            assert resp.json == {"Ping": "Pong"}

    def test_post_no_credentials(self, client):

        resp = client.simulate_post(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get BAD REQUEST
        assert resp.status == HTTP_BAD_REQUEST

    def test_post_empty_credentials(self, client):
        # test with empty credentials
        credentials = dict()

        resp = client.simulate_post(
            path=self.url,
            json=credentials,
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get BAD REQUEST
        assert resp.status == HTTP_BAD_REQUEST

    def test_post_shorted_password(self, client):
        # test with short password, less than 8 characters
        credentials = {
            "username": self.user.username,
            "password": self.password_string[:7],
        }

        resp = client.simulate_post(
            path=self.url,
            json=credentials,
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get UNPROCESSABLE_ENTITY
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY
        assert resp.json.get("description") == \
            "{'password': ['Length must be between 8 and 40.']}"

    def test_post_scrambled_password(self, client):
        # test with scrambled password with exact same length
        credentials = {
            "username": self.user.username,
            "password": self.password_string[:-2] + generate_chars(2),
        }

        resp = client.simulate_post(
            path=self.url,
            json=credentials,
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get UNAUTHORIZED
        assert resp.status == HTTP_UNAUTHORIZED
        assert resp.json.get("code") == 88811  # creds received but invalid

    def test_post_scrambled_username_and_password(self, client):
        # test with both scrambled username and password
        credentials = {
            "username": self.user.username[:-2] + generate_chars(2),
            "password": self.password_string[:-5] + generate_chars(5),
        }

        resp = client.simulate_post(
            path=self.url,
            json=credentials,
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get UNAUTHORIZED
        assert resp.status == HTTP_UNAUTHORIZED
        assert resp.json.get("code") == 88811

    def test_post_valid_credentials(self, client, request):

        # login with valid credentials
        credentials = {
            "username": self.user.username,
            "password": self.password_string,
        }

        resp = client.simulate_post(
            path=self.url,
            json=credentials,
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get OK
        assert resp.status == HTTP_OK

        # and get those tokens
        access_token = resp.json.get("access_token")
        refresh_token = resp.json.get("refresh_token")

        # then cache them
        request.config.cache.set("access_token", access_token)
        request.config.cache.set("refresh_token", refresh_token)

    def test_post_valid_credentials_as_form_urlencoded(self, client, request):
        # post as www-url-encoded content
        headers = self.headers
        headers.update(
            {"Content-Type": "application/x-www-form-urlencoded"}
        )

        # login with valid credentials
        credentials = {
            "username": self.user.username,
            "password": self.password_string,
        }

        resp = client.simulate_post(
            path=self.url,
            body=parse.urlencode(credentials),
            headers=headers,
            protocol=self.scheme,
        )

        access_token = resp.json.get("access_token")

        # should get OK
        assert resp.status == HTTP_OK

        # should pass
        assert access_token == user_authentication.check_token(access_token)

    def test_post_valid_credentials_as_basic_auth(self, client, request):
        # post credential as Basic Auth
        headers = self.headers

        # login with valid credentials
        credentials = ":".join([self.user.username, self.password_string])

        auth_string = "Basic %s" % \
            base64.encodebytes(bytes(credentials, 'utf8'))[:-1].decode('utf8')

        headers.update(
            {"AUTHORIZATION": auth_string}
        )
        resp = client.simulate_post(
            path=self.url,
            headers=headers,
            protocol=self.scheme,
        )

        access_token = resp.json.get("access_token")

        # should get OK
        assert resp.status == HTTP_OK

        # should equal
        assert access_token == user_authentication.check_token(access_token)

    def test_post_verify_without_access_token(self, client, request):

        # no access_token payload
        resp = client.simulate_post(
            path=self.url + "/verify",
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get BAD REQUEST
        assert resp.status == HTTP_BAD_REQUEST

        # empty dict
        payload = {}

        resp = client.simulate_post(
            path=self.url + "/verify",
            json=payload,
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get BAD REQUEST
        assert resp.status == HTTP_BAD_REQUEST

    def test_post_verify_valid_access_token(self, client, request):
        # Veriy token whether it is valid or not

        # get cached token from previous login
        access_token = request.config.cache.get("access_token", None)

        payload = {"access_token": access_token}

        resp = client.simulate_post(
            path=self.url + "/verify",
            json=payload,
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get OK and get token as cached one
        assert resp.status == HTTP_OK
        assert resp.json.get("access_token") == access_token

    def test_post_varify_tampered_access_token(self, client, request):

        # get cached token from previous login
        access_token = request.config.cache.get("access_token", None)

        # tamper the token
        broken_token = access_token[:-2]

        payload = {"access_token": broken_token}

        resp = client.simulate_post(
            path=self.url + "/verify",
            json=payload,
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get UNAUTHORIZED
        assert resp.status == HTTP_UNAUTHORIZED

        # not token
        payload = {"not_token": "aiou"}

        resp = client.simulate_post(
            path=self.url + "/verify",
            json=payload,
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get UNAUTHORIZED
        assert resp.status == HTTP_UNAUTHORIZED

    def test_post_refresh_valid_token_pair(self, client, request):

        cached_access_token = request.config.cache.get("access_token", None)
        cached_refresh_token = request.config.cache.get("refresh_token", None)

        # renew that cached tokens
        payload = {
            "access_token": cached_access_token,
            "refresh_token": cached_refresh_token
        }

        resp = client.simulate_post(
            path=self.url + "/refresh",
            json=payload,
            headers=self.headers,
            protocol=self.scheme,
        )

        new_access_token = resp.json.get("access_token")
        new_refresh_token = resp.json.get("refresh_token")

        # should get OK and different tokens
        assert resp.status == HTTP_OK
        assert new_access_token != cached_access_token
        assert new_refresh_token != cached_refresh_token

    def test_post_refresh_tampered_access_token(self, client, request):

        cached_access_token = request.config.cache.get("access_token", None)
        cached_refresh_token = request.config.cache.get("refresh_token", None)

        # tamper that cached access token
        payload = {
            "access_token": cached_access_token[:2] + generate_chars(2),
            "refresh_token": cached_refresh_token
        }

        resp = client.simulate_post(
            path=self.url + "/refresh",
            json=payload,
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get UNAUTHORIZED
        assert resp.status == HTTP_UNAUTHORIZED

    def test_post_refresh_tampered_refresh_token(self, client, request):

        cached_access_token = request.config.cache.get("access_token", None)
        cached_refresh_token = request.config.cache.get("refresh_token", None)

        # tamper that cached refresh token
        payload = {
            "access_token": cached_access_token,
            "refresh_token": cached_refresh_token[:2] + generate_chars(2)
        }

        resp = client.simulate_post(
            path=self.url + "/refresh",
            json=payload,
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get UNAUTHORIZED
        assert resp.status == HTTP_UNAUTHORIZED

    def test_post_refresh_with_no_tokens(self, client, request):

        # tamper that cached refresh token
        payload = {
            "not_token": "foo",
            "not_refresh_token": "bar"
        }

        resp = client.simulate_post(
            path=self.url + "/refresh",
            json=payload,
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get UNAUTHORIZED
        assert resp.status == HTTP_UNAUTHORIZED

    def test_post_refresh_with_payload(self, client, request):

        resp = client.simulate_post(
            path=self.url + "/refresh",
            headers=self.headers,
            protocol=self.scheme,
        )

        # should get BAD REQUEST
        assert resp.status == HTTP_BAD_REQUEST
