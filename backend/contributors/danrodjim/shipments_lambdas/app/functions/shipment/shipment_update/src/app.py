from app.common.python.common.authentication.require_role import require_role
from app.common.python.common.database.models import Shipment, UserRole as ur, ShipmentStatus as ss, ShipmentLocation
from app.common.python.common.database.database import get_session
from app.common.python.common.response.make_response import make_response
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

        user = event.get("claims")
        user_id = user.get("id")
        role = user.get("role")
        
        body = ShippingUpdateRequestSchema().load(json_body)

    except:
        return make_response(
            {"error": "Invalid JSON body"},
            HTTPStatus.BAD_REQUEST
        )
    
    with get_session() as session:
        shipment: Shipment = session.query(Shipment).filter_by(id=pid).first()

        if not shipment:
            return make_response(
                {"error": "Shipment not found"},
                HTTPStatus.NOT_FOUND
            )

        if role == ur.warehouse_staff:
            new_status = body.get("status")

            if new_status:
                current_status = shipment.status

                if new_status == current_status:
                    return make_response(
                        {"error": f"Shipment is already in status '{current_status}'"},
                        HTTPStatus.BAD_REQUEST
                    )

                if current_status == ss.created and new_status == ss.in_transit:
                    shipment.status = ss.in_transit
                    shipment.in_transit_at = datetime.now()
                    shipment.in_transit_by_id = shipment.assigned_carrier_id
                elif current_status == ss.in_transit and new_status == ss.delivered:
                    shipment.status = ss.delivered
                    shipment.delivered_at = datetime.now()
                    shipment.delivered_by_id = shipment.assigned_carrier_id
                elif current_status == ss.created and new_status == ss.delivered:
                    return make_response(
                        {"error": "Cannot move shipment from 'created' directly to 'delivered'"},
                        HTTPStatus.BAD_REQUEST
                    )
                elif current_status == ss.delivered:
                    return make_response(
                        {"error": "Cannot change status of a delivered shipment"},
                        HTTPStatus.BAD_REQUEST
                    )
                else:
                    return make_response(
                        {"error": f"Invalid status transition from '{current_status}' to '{new_status}'"},
                        HTTPStatus.BAD_REQUEST
                    )

        elif role == ur.carrier:
            if shipment.status != ss.in_transit:
                return make_response(
                    {"error": "Shipment is not in transit"},
                    HTTPStatus.FORBIDDEN
                )

            if shipment.assigned_carrier_id != user_id:
                return make_response(
                    {"error": "You are not the assigned carrier"},
                    HTTPStatus.FORBIDDEN
                )

            location = body.get("location")
            if location:
                session.add(
                    ShipmentLocation(
                        shipment_id=shipment.id,
                        postal_code=location
                    )
                )

        session.commit()

    return make_response(
        {"Success": True},
        HTTPStatus.OK
    )