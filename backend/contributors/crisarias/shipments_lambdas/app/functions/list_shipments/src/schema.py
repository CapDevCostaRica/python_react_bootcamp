from app.common.python.shared.domain.models import ShipmentStatus

from marshmallow import Schema, ValidationError, fields, validates_schema


class ShippingListRequestSchema(Schema):
    status = fields.Enum(
        ShipmentStatus,
        by_value=True,
        required=False,
        allow_none=True,
    )
