"""Authentication Test."""

import pytest
from muria import config, DEBUG
from falcon import (
    HTTP_OK
)


@pytest.mark.usefixtures("client")
class TestPing:

    def test_get_ping(self, client, request):

        # get cached token from previous login
        access_token = request.config.cache.get("access_token", "")

        prefix = config.get("jwt_header_prefix")
        self.headers.update({"Authorization": prefix + " " + access_token})
        self.headers.update({"Ping": "Ping"})

        resp = client.simulate_get(
            path="/v1/ping",
            headers=self.headers,
            protocol=self.scheme
        )

        assert resp.status == HTTP_OK
        assert resp.headers.get('Ping') == 'Pong'
        if DEBUG:
            assert resp.json == {"Ping": "Pong"}
