from marshmallow import Schema, fields
from app.common.python.common.database.models import ShipmentStatus


class DateRangeSchema(Schema):
    from_date = fields.DateTime(allow_none=True)
    to_date = fields.DateTime(allow_none=True)


class ShippingListRequestSchema(Schema):
    status = fields.String(allow_none=True)
    carrier = fields.Integer(allow_none=True)
    id = fields.Integer(allow_none=True)
    date = fields.Nested(DateRangeSchema, allow_none=True)


class ShippingListResponseSchema(Schema):
    results = fields.List(fields.Dict(), required=True)
    result_count = fields.Integer(required=True)


class ErrorSchema(Schema):
    error = fields.String(required=True)
