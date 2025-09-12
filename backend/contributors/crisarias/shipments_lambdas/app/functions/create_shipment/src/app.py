from app.common.python.shared.security.require_role import require_role
from app.common.python.shared.infrastructure.telemetry import logger
from app.common.python.shared.infrastructure.response import make_response
from .schema import ShipmentCreateRequestSchema
from .query import createShipment


import base64
import json
from http import HTTPStatus
from marshmallow import ValidationError

@require_role("warehouse_staff")
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
        user = context.get("user_claims")
        body = ShipmentCreateRequestSchema().load(body)
        carrier = body.get("carrier", "")
        originWareHouse = body.get("origin_warehouse", "")
        target_warehouse = body.get("target_warehouse", "")
    except ValidationError as e:
        logger.error(f"Validation error: {e.messages}")
        return make_response({"error": str(e)}, HTTPStatus.BAD_REQUEST)
    
    try:
        createResponse = createShipment(user, originWareHouse, target_warehouse, carrier)
        return createResponse[1]
    except Exception as e:
        logger.error(f"Internal error: {e}")
        return make_response({"error": "Internal Server Error"}, HTTPStatus.INTERNAL_SERVER_ERROR)