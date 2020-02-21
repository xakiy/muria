"""Profile Resource Test."""

import pytest
from muria import config
from pony.orm import db_session
from falcon import (
    HTTP_OK
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
        assert resp.json['profile'] == self.user.unload()
