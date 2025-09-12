from app.common.python.shared.domain.models import ShipmentStatus

from marshmallow import Schema, ValidationError, fields, validates


class ShippingUpdateStaffRequestSchema(Schema):
    status = fields.Enum(
        ShipmentStatus,
        by_value=True,
        required=True,
        allow_none=False,
        error_messages={"required": "Status is required", "null": "Status cannot be null"},
    )
        
class ShippingUpdateCarrierRequestSchema(Schema):
    location = fields.String(
        required=True,
        allow_none=False,
        error_messages={"required": "Location is required", "null": "Location cannot be null"},
    )

    @validates('location')
    def validate_resource(self, value, data_key: str):
        if not value or not value.strip():
            raise ValidationError(f'{data_key} cannot be empty.')
