import json
from http import HTTPStatus
from datetime import datetime
from marshmallow import ValidationError

from app.common.python.common.authentication.require_role import require_role
from app.common.python.common.response.make_response import make_response
from app.common.python.common.database.database import get_session
from app.common.python.common.database import models
from .schema import UpdateShipmentSchema

@require_role("carrier", "warehouse_staff")
def handler(event, context):

    claims = event.get("claims") or {}
    user_id = claims.get("sub")
    role = claims.get("role")


    shipment_id = event.get("pathParameters", {}).get("shipment_id")
    if not shipment_id:
        return make_response({"error": "Missing shipment ID in path"}, HTTPStatus.BAD_REQUEST)


    try:
        json_body = json.loads(event.get("body") or "{}")
    except Exception:
        return make_response({"error": "Invalid JSON body"}, HTTPStatus.BAD_REQUEST)

    with get_session() as session:

        shipment = session.query(models.Shipment).get(shipment_id)
        if not shipment:
            return make_response({"error": "Shipment not found."}, HTTPStatus.NOT_FOUND)

        previous_status = shipment.status


        try:
            schema = UpdateShipmentSchema(context={
                "role": role,
                "current_status": previous_status
            })
            payload = schema.load(json_body)
        except ValidationError as err:
            return make_response({"error": err.messages}, HTTPStatus.BAD_REQUEST)

        new_status = payload.get("status")
        location = payload.get("location")
        now = datetime.utcnow()

        if new_status == "in_transit" and previous_status == "created":
            shipment.status = "in_transit"
            shipment.in_transit_at = now
            shipment.in_transit_by_id = user_id
        elif new_status == "delivered" and previous_status == "in_transit":
            shipment.status = "delivered"
            shipment.delivered_at = now
            shipment.delivered_by_id = user_id

        if role == "carrier" and shipment.status == "in_transit" and shipment.assigned_carrier_id == user_id:
            if location:
                new_location = models.ShipmentLocation(
                    shipment_id=shipment.id,
                    postal_code=location,
                    noted_at=now
                )
                session.add(new_location)

        session.commit()

    response_message = f"Shipment {shipment_id} updated to '{shipment.status}' successfully."
    if location:
        response_message += f" Location '{location}' registered."

    return make_response({"message": response_message}, HTTPStatus.OK)
