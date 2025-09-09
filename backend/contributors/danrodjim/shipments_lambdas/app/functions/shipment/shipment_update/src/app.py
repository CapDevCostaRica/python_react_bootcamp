from app.common.python.common.authentication.require_role import require_role
from app.common.python.common.database.models import Shipment, UserRole as ur, ShipmentStatus as ss, ShipmentLocation
from app.common.python.common.database.database import get_session
from app.common.python.common.response.make_response import make_response
from app.common.python.common.authentication.jwt import decode_jwt
from ...schema import ShippingUpdateRequestSchema
from http import HTTPStatus
from datetime import datetime
import base64
import json

@require_role(ur.warehouse_staff, ur.carrier)
def handler(event, context):
    try:
        pid = (event.get("pathParameters") or {}).get("shipment_id")

        body = event.get("body") or {}

        if event.get("isBase64Enconded"):
            body = base64.b64decode(body).decode()

        json_body = json.loads(body)

        headers = event.get("headers") or {}
        auth_header = headers.get("Authorization", "")
            
        user = decode_jwt(auth_header.split(" ", 1)[1].strip())

        role = user.get("role")
        user_id = user.get("id")

        body = ShippingUpdateRequestSchema().load(json_body)

    except:
        return make_response(
            {"error": "Invalid JSON body"},
            HTTPStatus.BAD_REQUEST
        )
    
    with get_session() as session:
        shipment: Shipment = session.query(Shipment).filter_by(id=pid).first()
        if shipment:
            if role == ur.warehouse_staff:
                status = body.get("status")
                if status:
                    shipment.status = status
                    if status == "in_transit":
                        shipment.in_transit_at = datetime.now()
                        shipment.in_transit_by_id = shipment.assigned_carrier_id
                    elif status == "delivered":
                        shipment.delivered_at = datetime.now()
                        shipment.delivered_by_id = shipment.assigned_carrier_id
            elif role == ur.carrier:
                if shipment.status == ss.in_transit:
                    location = body.get("location")
                    if location:
                        session.add(ShipmentLocation(shipment_id = shipment.id, postal_code = location))
                        shipment.in_transit_at = datetime.now()
                        shipment.in_transit_by_id = user_id
                        shipment.assigned_carrier_id = user_id
                else:
                    return make_response(
                        {"error": "Shipment is not in transit"},
                        HTTPStatus.FORBIDDEN
                    )

        session.commit()

    return make_response(
        {"Success": True},
        HTTPStatus.OK
    )