from datetime import datetime
from flask import request
from app.common.python.common.decorators.require_role import require_role
from app.common.python.common.response.response import send_response
from app.common.python.common.database.models import Shipment, ShipmentStatus, UserRole, ShipmentLocation
from app.common.python.common.schema.shipping import UpdateShipmentSchema
from app.common.python.common.database.database import get_session
from http import HTTPStatus

@require_role([UserRole.carrier, UserRole.global_manager, UserRole.store_manager, UserRole.warehouse_staff])
def handler(event, context):
    json_body = request.get_json(silent=True) or {}
    user_data = event.get("user_data")
    params = event.get("pathParameters", {})
    shipment_id = params.get("shipment_id", 0)

    if not user_data:
        return send_response({ "error": "Invalid token" }, HTTPStatus.UNAUTHORIZED)
    
    if not shipment_id:
        return send_response({ "error": "Invalid shipment" }, HTTPStatus.NOT_FOUND)

    try:
        body = UpdateShipmentSchema().load(json_body)
    except Exception as e:
        return send_response({"error": str(e)}, HTTPStatus.BAD_REQUEST)

    with get_session() as db:
        shipment = db.query(Shipment).filter(Shipment.id == shipment_id).one_or_none()
        if not shipment:
            return send_response({"error": "Shipment not found"}, HTTPStatus.NOT_FOUND)

        new_status = body.get("status")
        new_location = body.get("location")
        logged_user_id = user_data.get("id")
        logged_user_role = user_data.get("role")

        if new_location:
            valid_logged_user = shipment.assigned_carrier_id == logged_user_id and logged_user_role == UserRole.carrier
            is_in_transit = shipment.status == ShipmentStatus.in_transit

            if  not is_in_transit or not valid_logged_user:
                return send_response({"error": "Only assigned carrier can update location of a in transit shipment "}, HTTPStatus.FORBIDDEN)

            new_shipment_location = ShipmentLocation(
                shipment_id = shipment.id,
                postal_code = new_location,
                noted_at = datetime.utcnow()
            )
            db.add(new_shipment_location)

        if new_status:
            if new_status == ShipmentStatus.in_transit:
                if shipment.status != ShipmentStatus.created:
                    return send_response({"error": "Can only set to In Transit from Created"}, HTTPStatus.FORBIDDEN)
                shipment.status = ShipmentStatus.in_transit
                shipment.in_transit_at = datetime.utcnow()
                shipment.in_transit_by_id = logged_user_id
            elif new_status == ShipmentStatus.delivered:
                if shipment.status != ShipmentStatus.in_transit:
                    return send_response({"error": "Can only deliver a shipment In Transit"}, HTTPStatus.FORBIDDEN)
                shipment.status = ShipmentStatus.delivered
                shipment.delivered_at = datetime.utcnow()
                shipment.delivered_by_id = logged_user_id

        db.commit()
        db.refresh(shipment)

        return send_response({"update": "ok"}, HTTPStatus.OK)
    
    return send_response({}, HTTPStatus.FORBIDDEN)
