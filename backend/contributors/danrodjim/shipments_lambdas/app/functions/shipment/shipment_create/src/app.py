from app.common.python.common.authentication.require_role import require_role
from app.common.python.common.database.models import Shipment, UserRole as ur, ShipmentLocation
from app.common.python.common.database.database import get_session
from app.common.python.common.response.make_response import make_response
from app.common.python.common.authentication.jwt import decode_jwt
from ...schema import ShippingCreateRequestSchema
from http import HTTPStatus
from datetime import datetime
import base64
import json

@require_role(ur.warehouse_staff)
def handler(event, context):
    try:
        body = event.get("body") or {}

        if event.get("isBase64Enconded"):
            body = base64.b64decode(body).decode()

        json_body = json.loads(body)

        headers = event.get("headers") or {}
        auth_header = headers.get("Authorization", "")
            
        user = decode_jwt(auth_header.split(" ", 1)[1].strip())

        user_id = user.get("id")

    except:
        return make_response(
            {"error": "Invalid JSON body"},
            HTTPStatus.BAD_REQUEST
        )
    
    body = ShippingCreateRequestSchema().load(json_body)

    new_shipment = Shipment(
        origin_warehouse_id = body.get("origin_warehouse"),
        destination_warehouse_id = body.get("target_warehouse"),
        assigned_carrier_id = body.get("carrier"),
        status = body.get("status"),
        created_at = datetime.now(),
        created_by_id = user_id
    )

    with get_session() as session:
        session.add(new_shipment)
        session.commit()
        shipment = session.query(Shipment).get(new_shipment.id)
        for location in body.get("shipment_locations"):
            session.add(ShipmentLocation(shipment_id = shipment.id, postal_code = location))
        session.commit()

    return make_response(
        {"Success": True},
        HTTPStatus.OK
    )