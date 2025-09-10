from marshmallow import Schema, fields, validates_schema, ValidationError
from app.common.python.common.database.models import ShipmentStatus


class UpdateShipmentRequestSchema(Schema):
    status = fields.String(allow_none=True)
    location = fields.String(allow_none=True)

    @validates_schema
    def validate_status_transition(self, data, **kwargs):
        status = data.get("status")
        if status and status not in ["created", "in_transit", "delivered"]:
            raise ValidationError("Invalid status. Must be one of: created, in_transit, delivered")


class UpdateShipmentResponseSchema(Schema):
    id = fields.Integer(required=True)
    status = fields.String(required=True)
    created_at = fields.String(required=True)
    in_transit_at = fields.String(allow_none=True)
    delivered_at = fields.String(allow_none=True)
    origin_warehouse_id = fields.Integer(required=True)
    destination_warehouse_id = fields.Integer(required=True)
    assigned_carrier_id = fields.Integer(required=True)
    created_by_id = fields.Integer(required=True)
    in_transit_by_id = fields.Integer(allow_none=True)
    delivered_by_id = fields.Integer(allow_none=True)


class ErrorSchema(Schema):
    error = fields.String(required=True)
