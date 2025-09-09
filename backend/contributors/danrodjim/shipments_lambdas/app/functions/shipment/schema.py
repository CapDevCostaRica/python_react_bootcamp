from marshmallow import Schema, fields
from app.common.python.common.database.models import ShipmentStatus

class ShippingListRequestSchema(Schema):
    status = fields.Enum(
        ShipmentStatus,
        by_value=True,
        required=False,
        allow_none=True,
    )
    carrier = fields.Integer(required=False)
    date = fields.Date(format='%Y-%m-%d')

class UserSchema(Schema):
    id = fields.Integer(required=True)
    username = fields.String(required=True)
    role = fields.String(required=True)

class WarehouseSchema(Schema):
    name = fields.String(required=True)
    postal_code = fields.String(required=True)

class ShipmentLocationSchema(Schema):
    postal_code = fields.String(required=True)
    noted_at = fields.String(required=True)

class ShipmentSchema(Schema):
    id = fields.Integer(required=True)
    status = fields.Enum(ShipmentStatus, by_value=True, required=True)
    created_at = fields.String(required=True)
    in_transit_at = fields.String(allow_none=True)
    delivered_at = fields.String(allow_none=True)
    origin_warehouse = fields.Nested(WarehouseSchema, required=True)
    target_warehouse = fields.Nested(WarehouseSchema, required=True)
    carrier = fields.Nested(UserSchema, required=True)
    created_by = fields.Nested(UserSchema, required=True)
    in_transit_by = fields.Nested(UserSchema, required=True)
    delivered_by = fields.Nested(UserSchema, required=True)
    shipment_locations = fields.List(
        fields.Nested(ShipmentLocationSchema), required=True
    )

class ShippingListResponseSchema(Schema):
    results = fields.List(fields.Nested(ShipmentSchema), required=True)
    result_count = fields.Integer(required=True)

class ShippingCreateRequestSchema(Schema):
    status = fields.Enum(ShipmentStatus, by_value=True, required=True)
    origin_warehouse = fields.Integer(required=True)
    target_warehouse = fields.Integer(required=True)
    carrier = fields.Integer(required=True)
    shipment_locations = fields.List(fields.String(required=True), required=True)

class ShippingUpdateRequestSchema(Schema):
    status = fields.Enum(ShipmentStatus, by_value=True, required=False)
    location = fields.String(required=False)