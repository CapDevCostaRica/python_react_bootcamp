from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    role = fields.Str(required=True, validate=validate.OneOf(["global_manager","store_manager","warehouse_staff","carrier"]))
    store_id = fields.Str(allow_none=True)
    carrier_id = fields.Str(allow_none=True)

class ShipmentSchema(Schema):
    id = fields.Int(dump_only=True)
    origin_store = fields.Str(required=True)
    destination_store = fields.Str(required=True)
    carrier_id = fields.Str(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(["created","in_transit","delivered"]))
    location = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)

class ShipmentCreateSchema(Schema):
    origin_store = fields.Str(required=True)
    destination_store = fields.Str(required=True)
    carrier_id = fields.Str(required=True)
    location = fields.Str(allow_none=True)

class ShipmentUpdateSchema(Schema):
    status = fields.Str(validate=validate.OneOf(["in_transit","delivered"]))
    location = fields.Str(allow_none=True)