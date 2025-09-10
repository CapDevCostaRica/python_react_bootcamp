from app.models import ShipmentStatus
from marshmallow import Schema, ValidationError, fields, validates_schema


class ErrorSchema(Schema):
    error = fields.String(required=True)


class LoginRequestSchema(Schema):
    username = fields.String(required=True)


class LoginResponseSchema(Schema):
    access_token = fields.String(required=True)
    token_type = fields.String(required=True)

class DateWindowSchema(Schema):
    from_date = fields.Date()
    to_date = fields.Date()

    @validates_schema
    def validate_range(self, data, **kwargs):
        if not data.get("from_date") and not data.get("to_date"):
            raise ValidationError("Please specify at least one date to filter the results.")
        if data.get("from_date") and data.get("to_date"):
            if data["from_date"] > data["to_date"]:
                raise ValidationError("The date range is invalid: start date must be earlier than end date.")

class ShippingListRequestSchema(Schema):
    status = fields.Enum(
        ShipmentStatus,
        by_value=True,
        required=False,
        allow_none=True,
    )
    carrier = fields.Integer(required=False)
    date = fields.Nested(DateWindowSchema, required=False)
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


class InvoiceListRequestSchema(Schema):
    number = fields.String(required=False)
    from_date = fields.Date(required=False)
    to_date = fields.Date(required=False)

    @validates_schema
    def validate_dates(self, data, **kwargs):
        from_date = data.get("from_date")
        to_date = data.get("to_date")

        if (from_date and not to_date) or (to_date and not from_date):
            raise ValidationError(
                "Both from_date and to_date must be provided if one is specified."
            )


class InvoiceSchema(Schema):
    id = fields.String(required=True)
    number = fields.String(required=True)
    date = fields.Date(required=True)
    amount = fields.Float(required=True)
    customer_id = fields.String(required=True)
    status = fields.String(required=True)


class InvoiceListResponseSchema(Schema):
    invoices = fields.List(fields.Nested(InvoiceSchema), required=True)
    count = fields.Integer(required=True)

class ShipmentCreateRequestSchema(Schema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    origin_warehouse_id = fields.Int(required=True)
    destination_warehouse_id = fields.Int(required=True)
    assigned_carrier_id = fields.Int(required=True)
    postal_code = fields.Str(required=False)

    @validates_schema
    def validate_ids(self, data, **kwargs):
        if data["origin_warehouse_id"] == data["destination_warehouse_id"]:
            raise ValidationError(
                "Origin and destination must be different.",
                field_name="destination_warehouse_id"
            )

        expected_origin = self.context.get("origin_warehouse_id")
        if expected_origin is not None and data["origin_warehouse_id"] != expected_origin:
            raise ValidationError(
                "You are only authorized to create shipments from your assigned warehouse.",
                field_name="origin_warehouse_id"
            )

class ShipmentUpdateRequestSchema(Schema):
    def __init__(self, *args, context=None, **kwargs):
        self.user_role = context.get("role") if context else None
        self.current_status = context.get("current_status") if context else None
        super().__init__(*args, **kwargs)

    status = fields.Str(required=False)
    location = fields.Str(required=False)

    @validates_schema
    def validate_status_transition(self, data, **kwargs):
        new_status = data.get("status")
        location = data.get("location")
        
        if not new_status:
            raise ValidationError("Missing data for required field.", field_name="status")

        if new_status not in ["in_transit", "delivered"]:
            raise ValidationError("Invalid status value", field_name="status")
        
        if self.user_role == "carrier":
            if new_status != "in_transit":
                raise ValidationError("Carriers can only mark shipments as 'in_transit'", field_name="status")

            if self.current_status == "in_transit":
                if location:
                    return
                raise ValidationError("Shipment is already in 'in_transit'. Provide location to update tracking.", field_name="status")

            if self.current_status == "created":
                return

            raise ValidationError("Shipment must be in 'created' state to mark as 'in_transit'", field_name="status")

        elif self.user_role == "warehouse_staff":
            if new_status != "delivered":
                raise ValidationError("Warehouse staff can only mark shipments as 'delivered'", field_name="status")
            if self.current_status != "in_transit":
                raise ValidationError("Shipment must be 'in_transit' to mark as 'delivered'", field_name="status")

        else:
            raise ValidationError("Unauthorized role for shipment update", field_name="status")