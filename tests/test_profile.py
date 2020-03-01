"""Profile Resource Test."""

import pytest
from muria import config
from pony.orm import db_session
from PIL import Image
from io import BytesIO
from tests import create_multipart
from falcon import (
    HTTP_OK,
    HTTP_CREATED,
    HTTP_BAD_REQUEST
)


@pytest.fixture(scope="class")
def url(request):
    request.cls.url = "/v1/profile"


@pytest.mark.usefixtures("client", "url")
class TestProfile():

    @db_session
    def test_get_profile(self, client, request):

        access_token = request.config.cache.get("access_token", "")
        prefix = config.get("jwt_header_prefix")
        self.headers.update({"Authorization": prefix + " " + access_token})

        resp = client.simulate_get(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme
        )
        # should be OK and match
        assert resp.status == HTTP_OK
        assert resp.json == self.user.unload()

    @db_session
    def test_edit_profile(self, client, request):

        access_token = request.config.cache.get("access_token", "")
        prefix = config.get("jwt_header_prefix")
        self.headers.update({"Authorization": prefix + " " + access_token})

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
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            json=user
        )

        # should be OK
        assert resp.status == HTTP_OK
        assert resp.json == user

        origin_user = self.user.unload()

        # restore default test user
        resp = client.simulate_patch(
            path=self.url,
            headers=self.headers,
            protocol=self.scheme,
            json=origin_user
        )

        # should be OK
        assert resp.status == HTTP_OK
        assert resp.json == origin_user

    @db_session
    def test_put_invalid_profile_picture_handler_name(self, client, request):

        resource_path = "/v1/profile/picture"

        access_token = request.config.cache.get("access_token", "")
        prefix = config.get("jwt_header_prefix")
        self.headers.update({"Authorization": prefix + " " + access_token})

        img = Image.new("RGB", (400, 300), color="green")
        bytes_stream = BytesIO()
        img.save(bytes_stream, "PNG")
        bytes_stream.seek(0)

        headers = self.headers.copy()

        # Create the multipart data and headers
        data, xheaders = create_multipart(
            bytes_stream.read(),
            # invalid handler name
            fieldname="profile_foo",
            filename="test.png",
            content_type="image/png",
        )

        headers.update(xheaders)

        resp = client.simulate_put(
            resource_path,
            headers=headers,
            protocol=self.scheme,
            body=data,
        )

        assert resp.status == HTTP_BAD_REQUEST

    @db_session
    def test_put_valid_profile_picture(self, client, request):

        resource_path = "/v1/profile/picture"

        access_token = request.config.cache.get("access_token", "")
        prefix = config.get("jwt_header_prefix")
        self.headers.update({"Authorization": prefix + " " + access_token})

        img = Image.new("RGB", (400, 300), color="green")
        bytes_stream = BytesIO()
        img.save(bytes_stream, "PNG")
        bytes_stream.seek(0)

        headers = self.headers.copy()

        # Create the multipart data and headers
        data, xheaders = create_multipart(
            bytes_stream.read(),
            fieldname="profile_picture",
            filename="test.png",
            content_type="image/png",
        )

        headers.update(xheaders)

        resp = client.simulate_put(
            resource_path,
            headers=headers,
            protocol=self.scheme,
            body=data,
        )

        assert resp.status == HTTP_CREATED
        # assert resp.json == 'foo'

    @db_session
    def test_get_profile_picture(self, client, request):
        resource_path = "/v1/profile/picture"

        access_token = request.config.cache.get("access_token", "")
        prefix = config.get("jwt_header_prefix")
        self.headers.update({"Authorization": prefix + " " + access_token})

        resp = client.simulate_get(
            resource_path,
            headers=self.headers,
            protocol=self.scheme
        )

        assert resp.status == HTTP_OK
