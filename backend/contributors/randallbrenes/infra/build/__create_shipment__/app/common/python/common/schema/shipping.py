import enum
from marshmallow import Schema, ValidationError, fields, validates_schema

class ShipmentStatus(str, enum.Enum):
    created = "created"
    in_transit = "in_transit"
    delivered = "delivered"

class DateRangeSchema(Schema):
    from_date = fields.Date(required=False)
    to_date = fields.Date(required=False)

    @validates_schema
    def validate_dates(self, data, **kwargs):
        from_date = data.get("from_date")
        to_date = data.get("to_date")

        if not to_date and not from_date:
            raise ValidationError(
                "Should provide a date"
            )

class ShippingListRequestSchema(Schema):
    status = fields.Enum(
        ShipmentStatus,
        by_value=True,
        required=False,
        allow_none=True,
    )
    date = fields.Nested(DateRangeSchema, required=False)
    carrier = fields.Integer(required=False)
    id = fields.Integer(required=False)


class UserSchema(Schema):
    username = fields.String(required=True)


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

class CreateShipmentSchema(Schema):
    target_warehouse = fields.Integer(required=True)
    carrier = fields.Integer(required=True)
    class Meta:
        unknown = "EXCLUDE"

class UpdateShipmentSchema(Schema):
    location = fields.String(required=False)
    status = fields.Enum(
        ShipmentStatus,
        by_value=True,
        required=False,
        allow_none=True,
    )
    class Meta:
        unknown = "EXCLUDE"
        
    @validates_schema
    def validate_some(self, data, **kwargs):
        location = data.get("location")
        status = data.get("status")

        if not location and not status:
            raise ValidationError(
                "Should provide a status or location to update"
            )