"""Ping Resource."""

from muria.common.resource import Resource
from falcon import (
    HTTP_OK
)


class Pong(Resource):
    """Users Stats."""

    def on_get(self, req, resp):
        """Ping End Point.
        ---
        tags:
        - ping
        summary: Ping end point
        operationId: ping
        parameters:
            - in: header
              name: origin
              type: string
              required: true
              description: CORS request origin
        responses:
            200:
                description: Ping response
        """

        ping = req.get_header('Ping')

        if ping and ping.lower() == 'ping':
            resp.status = HTTP_OK
            resp.set_header("Ping", "Pong")
            if self.config.getboolean("app", "debug"):
                resp.media = {"Ping": "Pong"}
