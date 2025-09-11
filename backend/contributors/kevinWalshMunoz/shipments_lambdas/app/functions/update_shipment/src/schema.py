from marshmallow import Schema, fields, validates_schema, ValidationError
from app.common.python.common.database.models import ShipmentStatus


class UpdateShipmentSchema(Schema):
    status = fields.String(required=False)
    location = fields.String(required=False)
    
    @validates_schema
    def validate_role_permissions(self, data, **kwargs):
        context = self.context
        role = context.get("role")
        current_status = context.get("current_status")
        
        # Validate based on role
        if role == "warehouse_staff":
            # Warehouse staff can only update status
            if "location" in data:
                raise ValidationError("Warehouse staff cannot update location")
                
            # Validate status transitions
            if "status" in data:
                new_status = data["status"]
                if new_status not in ["in_transit", "delivered"]:
                    raise ValidationError("Invalid status value")
                
                if new_status == "in_transit" and current_status != "created":
                    raise ValidationError("Can only mark as in_transit from created status")
                
                if new_status == "delivered" and current_status != "in_transit":
                    raise ValidationError("Can only mark as delivered from in_transit status")
        
        elif role == "carrier":
            # Carrier can only update location when shipment is in transit
            if "status" in data:
                raise ValidationError("Carrier cannot update status")
            
            if current_status != "in_transit" and "location" in data:
                raise ValidationError("Can only update location when shipment is in transit")
            
        # Ensure at least one field is provided
        if not data:
            raise ValidationError("No update fields provided")
            
        return data
