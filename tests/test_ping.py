"""Authentication Test."""

import pytest
from muria.init import DEBUG
from falcon import (
    HTTP_OK
)


@pytest.mark.usefixtures("client")
class TestPing:

    def test_get_ping(self, client):

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
