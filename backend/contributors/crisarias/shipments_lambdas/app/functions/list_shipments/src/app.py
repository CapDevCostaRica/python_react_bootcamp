# from app.common.python.shared.security.jwt import encode_jwt
from app.common.python.shared.security.require_role import require_role
from app.common.python.shared.infrastructure.telemetry import logger
 # from app.common.python.shared.domain.models import User
from app.common.python.shared.infrastructure.response import make_response
from .schema import ShippingListRequestSchema
from .query import shipment_list_by_role_and_status


import base64
import json
from http import HTTPStatus
from marshmallow import ValidationError

@require_role("global_manager", "store_manager", "warehouse_manager", "carrier")
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
        body = ShippingListRequestSchema().load(body)
        status = body.get("status", "")
    except ValidationError as e:
        logger.error(f"Validation error: {e.messages}")
        return make_response({"error": str(e)}, HTTPStatus.BAD_REQUEST)
    
    try:
        shipments = shipment_list_by_role_and_status(context.get("user_claims"), status)
        return make_response({
            "results": shipments,
            "result_count": len(shipments)
        }, HTTPStatus.OK)
    except Exception as e:
        logger.error(f"Internal error: {e}")
        return make_response({"error": "Internal Server Error"}, HTTPStatus.INTERNAL_SERVER_ERROR)