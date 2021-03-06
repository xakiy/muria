"""Marshmallow Schemas for Model Entities."""

import re
import uuid
from marshmallow import (
    Schema as _Schema,
    fields,
    EXCLUDE
)
from marshmallow.validate import Length, Regexp, OneOf
from muria.util import json


class Schema(_Schema):
    class Meta:
        # NOTE: Since Marshmallow 3.xx json_module is
        #        renamed to render_modul
        render_module = json
        unknown = EXCLUDE


class UID(fields.UUID):
    """A UUID field."""

    def _serialize(self, value, attr, obj):
        validated = str(self._validated(value)) if value is not None else None
        return str(validated)

    def _deserialize(self, value, attr, obj, **kwargs):
        validated = str(self._validated(value)) if value is not None else None
        return str(validated)


class Tanggal(fields.Date):
    """Bare ISO8601-formatted date string without time. """

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        try:
            return value.isoformat()[:10]
        except AttributeError:
            self.fail("format", input=value)
        return value


class Surel(fields.Email):
    def _deserialize(self, value, attr, obj, **kwargs):
        if not value:
            return ""
        return str(value).lower()


class Credentials(Schema):
    # min length is 8, max length is 30
    username = fields.String(
        required=True,
        validate=Regexp(r"^[a-z]+(?:[_.]?[a-zA-Z0-9]){7,28}$", re.U & re.I),
    )
    password = fields.String(validate=Length(min=8, max=40), load_only=True)


class User(Credentials):
    id = UID(required=True, default=uuid.uuid4)
    nama = fields.String(required=True)
    jinshi = fields.String(required=True, validate=OneOf(["l", "p"]))
    tempat_lahir = fields.String()
    tanggal_lahir = Tanggal(allow_none=True)
    tanggal_masuk = Tanggal()
    situs = fields.URL(allow_none=True, missing=None)
    email = Surel(required=True)
    suspended = fields.Boolean(default=False, dump_only=True)


class BaseToken(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)
    token_type = fields.String(required=True)
    issued_at = fields.String()
    expires_in = fields.Integer()
    refresh_expires_in = fields.Integer(load_only=True)


class JwtToken(BaseToken):
    user = User()
    access_key = fields.String(size=43, load_only=True)
    refresh_key = fields.String(size=43, load_only=True)
