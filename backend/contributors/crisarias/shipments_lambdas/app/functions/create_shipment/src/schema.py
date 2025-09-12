from app.common.python.shared.domain.models import ShipmentStatus

from marshmallow import Schema, ValidationError, fields, validates

class ShipmentCreateRequestSchema(Schema):
    origin_warehouse = fields.Integer(required=True, error_messages={"required": "Origin warehouse is required"})
    target_warehouse = fields.Integer(required=True, error_messages={"required": "Target warehouse is required"})
    carrier = fields.Integer(required=True, error_messages={"required": "Carrier is required"})