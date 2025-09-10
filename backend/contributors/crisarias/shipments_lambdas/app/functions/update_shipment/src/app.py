from app.common.python.shared.domain.models import UserRole
from app.common.python.shared.security.require_role import require_role
from app.common.python.shared.infrastructure.telemetry import logger
from app.common.python.shared.infrastructure.response import make_response
from .schema import ShippingUpdateStaffRequestSchema, ShippingUpdateCarrierRequestSchema
from .query import validatesShipmentAccess, UpdateShipment


import base64
import json
from http import HTTPStatus
from marshmallow import ValidationError

@require_role("warehouse_staff", "carrier")
def handler(event, context):
    # Extract username and password from the event
    try:
        body = event.get("body", {})

        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode("utf-8")

        body = json.loads(body)
    except:
        logger.error("Failed to parse request body")
        return make_response({"error": "Invalid request body"}, HTTPStatus.BAD_REQUEST)
    
    try:
        shipmentID = int(event.get("pathParameters", {}).get("shipment_id", ""))
        if not shipmentID:
            logger.error("Shipment ID is required")
            return make_response({"error": "Shipment ID is required"}, HTTPStatus.BAD_REQUEST)
    except ValueError:
        logger.error("Invalid shipment ID")
        return make_response({"error": "Invalid shipment ID"}, HTTPStatus.BAD_REQUEST)

    try:
        user = context.get("user_claims")
        isWarehouseStaff = user.get("role") == UserRole.warehouse_staff
        body = ShippingUpdateStaffRequestSchema().load(body) if isWarehouseStaff else ShippingUpdateCarrierRequestSchema().load(body)
        status = body.get("status", "")
        location = body.get("location", "")
    except ValidationError as e:
        logger.error(f"Validation error: {e.messages}")
        return make_response({"error": str(e)}, HTTPStatus.BAD_REQUEST)
    
    try:
        validationResponse = validatesShipmentAccess(user, shipmentID, status, location)
        if not validationResponse[0]:
            return validationResponse[1]
        updateResponse = UpdateShipment(user, validationResponse[1].get("shipment"), status, location)
        return updateResponse[1]
    except Exception as e:
        logger.error(f"Internal error: {e}")
        return make_response({"error": "Internal Server Error"}, HTTPStatus.INTERNAL_SERVER_ERROR)