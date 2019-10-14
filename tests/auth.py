"""Authentication Test."""

from muria.init import config, DEBUG, user_authentication
from muria.util.json import dumpAsJSON
from muria.util.misc import generate_chars
from falcon import (
    HTTP_UNPROCESSABLE_ENTITY,
    HTTP_UNAUTHORIZED,
    HTTP_OK
)


class Auth(object):

    def test_get_auth(self, client):

        url = "/v1/auth"

        headers = {
            "Content-Type": "application/json",
            "Host": config.get("security", "issuer"),
            "Origin": config.get("security", "audience"),
        }

        resp = client.simulate_get(
            path=url,
            headers=headers,
            protocol=self.protocol
        )

        assert resp.status == HTTP_OK
        assert resp.headers.get('www-authenticate') == 'Bearer'
        if DEBUG:
            assert resp.json == {"WWW-Authenticate": "Bearer"}

    def test_post_invalid_credentials(self, client):

        url = "/v1/auth"

        headers = {
            "Content-Type": "application/json",
            "Host": config.get("security", "issuer"),
            "Origin": config.get("security", "audience"),
        }

        # test with short password, less than 8 characters
        credentials = {
            "username": self.user.username,
            "password": self.password_string[:7],
        }

        resp = client.simulate_post(
            path=url,
            body=dumpAsJSON(credentials),
            headers=headers,
            protocol=self.protocol,
        )

        # should get UNPROCESSABLE_ENTITY
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY
        assert resp.json.get("description") == \
            "{'password': ['Length must be between 8 and 40.']}"

        # test with scrambled password with exact same length
        credentials = {
            "username": self.user.username,
            "password": self.password_string[:-2] + generate_chars(2),
        }

        resp = client.simulate_post(
            path=url,
            body=dumpAsJSON(credentials),
            headers=headers,
            protocol=self.protocol,
        )

        # should get UNAUTHORIZED
        assert resp.status == HTTP_UNAUTHORIZED
        assert resp.json.get("code") == 88811  # creds received but invalid

        # test with both scrambled username and password
        credentials = {
            "username": self.user.username[:-2] + generate_chars(2),
            "password": self.password_string[:-5] + generate_chars(5),
        }

        resp = client.simulate_post(
            path=url,
            body=dumpAsJSON(credentials),
            headers=headers,
            protocol=self.protocol,
        )

        # should get UNAUTHORIZED
        assert resp.status == HTTP_UNAUTHORIZED
        assert resp.json.get("code") == 88811

    def test_post_valid_credentials(self, client, request):

        url = "/v1/auth"

        headers = {
            "Content-Type": "application/json",
            "Host": config.get("security", "issuer"),
            "Origin": config.get("security", "audience"),
        }

        # login with valid credentials
        credentials = {
            "username": self.user.username,
            "password": self.password_string,
        }

        resp = client.simulate_post(
            path=url,
            body=dumpAsJSON(credentials),
            headers=headers,
            protocol=self.protocol,
        )

        # should get OK
        assert resp.status == HTTP_OK

        # and getting tokens
        access_token = resp.json.get("access_token")
        refresh_token = resp.json.get("refresh_token")

        # then cache them
        request.config.cache.set("access_token", access_token)
        request.config.cache.set("refresh_token", refresh_token)

        # should pass
        assert access_token == user_authentication.check_token(access_token)

    def test_post_verify_access_token(self, client, request):
        # Veriy token whether it is valid or not

        # get cached token from previous login
        access_token = request.config.cache.get("access_token", None)

        url = "/v1/auth/verify"

        headers = {
            "Content-Type": "application/json",
            "Host": config.get("security", "issuer"),
            "Origin": config.get("security", "audience"),
        }

        payload = {"access_token": access_token}

        resp = client.simulate_post(
            path=url,
            body=dumpAsJSON(payload),
            headers=headers,
            protocol=self.protocol,
        )

        # should get OK and the exact as cached token
        assert resp.status == HTTP_OK
        assert resp.json.get("access_token") == access_token

        # tamper the token
        broken_token = access_token[:-2]

        payload = {"access_token": broken_token}

        resp = client.simulate_post(
            "/v1/auth/verify",
            body=dumpAsJSON(payload),
            headers=headers,
            protocol=self.protocol,
        )

        # should get UNAUTHORIZED
        assert resp.status == HTTP_UNAUTHORIZED

    def test_post_refresh_tokens(self, client, request):

        cached_access_token = request.config.cache.get("access_token", None)
        cached_refresh_token = request.config.cache.get("refresh_token", None)

        url = "/v1/auth/refresh"

        headers = {
            "Content-Type": "application/json",
            "Host": config.get("security", "issuer"),
            "Origin": config.get("security", "audience"),
        }

        # renew that cached tokens
        payload = {
            "access_token": cached_access_token,
            "refresh_token": cached_refresh_token
        }

        resp = client.simulate_post(
            path=url,
            body=dumpAsJSON(payload),
            headers=headers,
            protocol=self.protocol,
        )

        new_access_token = resp.json.get("access_token")
        new_refresh_token = resp.json.get("refresh_token")

        # should get OK and different tokens
        assert resp.status == HTTP_OK
        assert new_access_token != cached_access_token
        assert new_refresh_token != cached_refresh_token
