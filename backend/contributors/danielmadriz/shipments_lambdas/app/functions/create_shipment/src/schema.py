from marshmallow import Schema, fields, validates_schema, ValidationError
from app.common.python.common.database.models import ShipmentStatus


class CreateShipmentRequestSchema(Schema):
    origin_warehouse_id = fields.Integer(required=True)
    destination_warehouse_id = fields.Integer(required=True)
    assigned_carrier_id = fields.Integer(required=True)

    @validates_schema
    def validate_warehouses(self, data, **kwargs):
        if data.get("origin_warehouse_id") == data.get("destination_warehouse_id"):
            raise ValidationError("Origin and destination warehouses cannot be the same")
        
        # Validate that origin_warehouse_id matches the user's warehouse
        context_warehouse_id = self.context.get("origin_warehouse_id")
        if context_warehouse_id and data.get("origin_warehouse_id") != context_warehouse_id:
            raise ValidationError("You can only create shipments from your assigned warehouse")


class CreateShipmentResponseSchema(Schema):
    id = fields.Integer(required=True)
    status = fields.String(required=True)
    created_at = fields.String(required=True)
    origin_warehouse_id = fields.Integer(required=True)
    destination_warehouse_id = fields.Integer(required=True)
    assigned_carrier_id = fields.Integer(required=True)
    created_by_id = fields.Integer(required=True)


class ErrorSchema(Schema):
    error = fields.String(required=True)
