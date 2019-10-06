"""Testing Account Resource."""

import pytest
import falcon
import hashlib

from pony.orm import db_session

# from urllib.parse import urlencode

from muria.init import config
from muria.lib.misc import dumpAsJSON
from tests._pickles import _unpickling
from tests._data_generator import DataGenerator


class Profile(object):
    @db_session
    def get_profile(self, client, request):

        resource_path = "/v1/profile"

        access_token = request.config.cache.get("access_token", None)

        # headers updated based on header requirements
        headers = {
            "Content-Type": "application/json",
            "Host": config.get("security", "issuer"),
            "Origin": config.get("security", "audience"),
            "Authorization": "Bearer " + access_token,
        }

        resp = client.simulate_get(
            resource_path, headers=headers, protocol=self.protocol
        )

        self.content = resp.json.get("account")
        request.config.cache.set("muria/account_content", self.content)

        assert resp.status == falcon.HTTP_OK
        assert self.content.get("email") == self.user.email
        assert self.content.get("username") == self.user.username
        assert self.content.get("profile")["id"] == self.orang.id
        assert self.content.get("profile")["nama"] == self.orang.nama

    @db_session
    def put_profile_picture(self, client, request):

        from PIL import Image
        from io import BytesIO, BufferedReader
        from tests._lib import create_multipart

        resource_path = "/v1/profile/picture"

        access_token = request.config.cache.get("access_token", None)

        img = Image.new("RGB", (400, 300), color="green")
        # bytes_stream = BufferedReader()
        bytes_stream = BytesIO()
        img.save(bytes_stream, "PNG")
        bytes_stream.seek(0)

        # Create the multipart data
        data, headers = create_multipart(
            bytes_stream.read(),
            fieldname="profile_image",
            filename="pict_test.png",
            content_type="image/png",
        )

        # headers updated based on header requirements
        headers.update(
            {
                "Host": config.get("security", "issuer"),
                "Origin": config.get("security", "audience"),
                "Authorization": "Bearer " + access_token,
            }
        )

        resp = client.simulate_put(
            resource_path, body=data, headers=headers, protocol=self.protocol
        )

        assert resp.status == falcon.HTTP_CREATED
        # assert resp.headers.get('location') == 'foo'
        # assert resp.json.get('success') == 'foo'

    @db_session
    def get_profile_picture(self, client, request):
        resource_path = "/v1/profile/picture"

        access_token = request.config.cache.get("access_token", None)
        headers = {
            "Host": config.get("security", "issuer"),
            "Origin": config.get("security", "audience"),
            "Authorization": "Bearer " + access_token,
        }

        resp = client.simulate_get(
            resource_path, headers=headers, protocol=self.protocol
        )

        assert resp.status == falcon.HTTP_OK

    @db_session
    def edit_profile(self, client, request):

        account_content = request.config.cache.get("muria/account_content", None)

        if account_content is not None:
            mod_content = account_content.copy()
            # putting id in parent data
            mod_content["id"] = mod_content["profile"]["id"]

            # reversing user in email
            old_email = mod_content["email"].split("@")
            ori_nama = mod_content["profile"]["nama"].split(" ")
            ori_nama.reverse()
            nama = (".").join(ori_nama)
            new_email = nama + "@" + old_email[-1:].pop()

            assert mod_content["email"] != new_email

            mod_content["email"] = new_email

            # reversing username
            new_username = mod_content["username"].split(".")
            new_username.reverse()
            new_username = (".").join(new_username)

            assert mod_content["username"] != new_username

            mod_content["username"] = new_username

            resource_path = "/v1/profile"

            access_token = request.config.cache.get("access_token", None)

            # headers updated based on header requirements
            headers = {
                "Content-Type": "application/json",
                "Host": config.get("security", "issuer"),
                "Origin": config.get("security", "audience"),
                "Authorization": "Bearer " + access_token,
            }

            resp = client.simulate_patch(
                resource_path,
                body=dumpAsJSON(mod_content),
                headers=headers,
                protocol=self.protocol,
            )

            assert resp.status == falcon.HTTP_OK

            response = resp.json.get("account")

            assert response["email"] != account_content["email"]
            assert response["username"] != account_content["username"]

            # restore default user data
            account_content["id"] = account_content["profile"]["id"]

            resp = client.simulate_patch(
                resource_path,
                body=dumpAsJSON(account_content),
                headers=headers,
                protocol=self.protocol,
            )

            assert resp.status == falcon.HTTP_OK

            response = resp.json.get("account")

            assert response["email"] == account_content["email"]
            assert response["username"] == account_content["username"]

    @db_session
    def change_account_password(self, client, request):

        resource_path = "/v1/profile/security"

        access_token = request.config.cache.get("access_token", None)

        new_pass = DataGenerator().randomChar(10)

        data = {"old_password": self.password_string, "new_password": new_pass}

        # headers updated based on header requirements
        headers = {
            "Content-Type": "application/json",
            "Host": config.get("security", "issuer"),
            "Origin": config.get("security", "audience"),
            "Authorization": "Bearer " + access_token,
        }

        resp = client.simulate_patch(
            resource_path,
            body=dumpAsJSON(data),
            headers=headers,
            protocol=self.protocol,
        )

        assert resp.status == falcon.HTTP_CREATED

        # restore original data

        data = {"new_password": self.password_string, "old_password": new_pass}

        headers = {
            "Content-Type": "application/json",
            "Host": config.get("security", "issuer"),
            "Origin": config.get("security", "audience"),
            "Authorization": "Bearer " + access_token,
        }

        resp = client.simulate_patch(
            resource_path,
            body=dumpAsJSON(data),
            headers=headers,
            protocol=self.protocol,
        )

        assert resp.status == falcon.HTTP_CREATED
