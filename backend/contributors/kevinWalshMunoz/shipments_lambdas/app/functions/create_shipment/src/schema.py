from marshmallow import Schema, ValidationError, fields, validates_schema

from app.common.python.common.database.models import ShipmentStatus


class ErrorSchema(Schema):
    error = fields.String(required=True)


class CreateShipmentRequestSchema(Schema):
    origin_warehouse_id = fields.Integer(required=True)
    destination_warehouse_id = fields.Integer(required=True)
    assigned_carrier_id = fields.Integer(required=True)


class CreateShipmentResponseSchema(Schema):
    id = fields.Integer(required=True)
    status = fields.Enum(ShipmentStatus, by_value=True, required=True)
    created_at = fields.String(required=True)
    origin_warehouse_id = fields.Integer(required=True)
    destination_warehouse_id = fields.Integer(required=True)
    assigned_carrier_id = fields.Integer(required=True)
    created_by_id = fields.Integer(required=True)
