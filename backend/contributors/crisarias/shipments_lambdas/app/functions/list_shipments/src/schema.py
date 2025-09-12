from app.common.python.shared.domain.models import ShipmentStatus

from marshmallow import Schema, ValidationError, fields, validates_schema


class ShippingListRequestSchema(Schema):
    status = fields.Enum(
        ShipmentStatus,
        by_value=True,
        required=False,
        allow_none=True,
    )
    carrier = fields.Int(required=False, allow_none=True)
    id = fields.Int(required=False, allow_none=True)
    startDate = fields.DateTime(required=False, allow_none=True)
    endDate = fields.DateTime(required=False, allow_none=True)
