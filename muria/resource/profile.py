"""Profile."""

import falcon
from . import Resource


class Profile(Resource):

    def on_get(self, req, resp, **params):
        resp.media = {'msg': 'hi, there!'}
        resp.status = falcon.HTTP_OK

    def on_post(self, req, resp, **params):
        resp.media = {'msg': 'got posted!'}
        resp.status = falcon.HTTP_OK
