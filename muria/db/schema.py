from marshmallow import Schema, fields, validate
from marshmallow.validate import Length, Regexp
import re
import json
import uuid


class Skema(Schema):
    class Meta:
        json_module = json


class UID(fields.UUID):
    """A UUID field."""

    def _serialize(self, value, attr, obj):
        validated = str(self._validated(value)) if value is not None else None
        return str(validated)

    def _deserialize(self, value, attr, obj):
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
    def _deserialize(self, value, attr, obj):
        if not value:
            return ""
        return str(value).lower()


class _Bio(Skema):
    id = UID(required=True, default=uuid.uuid4)
    nama = fields.String(required=True)
    jinshi = fields.String(required=True, validate=validate.OneOf(["l", "p"]))
    tempat_lahir = fields.String()
    tanggal_lahir = Tanggal(allow_none=True)
    tanggal_masuk = Tanggal()


class _User(Skema):
    id = UID(required=True, default=uuid.uuid4)
    profile = fields.Nested("_Bio", only=("id", "nama", "jinshi"))
    username = fields.String(
        required=True,
        validate=Regexp(r"^[a-z]+(?:[_.]?[a-zA-Z0-9]){7,28}$", re.U & re.I),
    )
    email = Surel(missing=None, allow_none=True)
    password = fields.String(validate=Length(min=8, max=40), load_only=True)
    suspended = fields.Boolean(required=True, missing=False)


class _Credentials(Skema):
    username = fields.String(
        required=True,
        validate=Regexp(r"^[a-z]+(?:[_.]?[a-zA-Z0-9]){7,28}$", re.U & re.I),
    )
    password = fields.String(validate=Length(min=8, max=40), load_only=True)
