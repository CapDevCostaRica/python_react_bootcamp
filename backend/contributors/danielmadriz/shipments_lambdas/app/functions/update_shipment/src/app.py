from app.common.python.common.authentication.require_role import require_role
from app.common.python.common.database.database import get_session
from app.common.python.common.database import models
from app.common.python.common.response import make_response
from http import HTTPStatus
from .schema import UpdateShipmentRequestSchema, UpdateShipmentResponseSchema, ErrorSchema
from marshmallow import ValidationError
from datetime import datetime, timezone

import json
import logging

logger = logging.getLogger(__name__)


@require_role("warehouse_staff", "carrier")
def handler(event, context):
    claims = event.get("claims") or {}
    role = claims.get("role")
    user_id = int(claims.get("sub")) if claims.get("sub") else None
    warehouse_id = int(claims.get("warehouse_id")) if claims.get("warehouse_id") else None

    logger.info(f"Update shipment handler called - role: {role}, user_id: {user_id}, warehouse_id: {warehouse_id}")

    shipment_id = event.get("pathParameters", {}).get("shipment_id")
    if not shipment_id:
        return make_response(
            {"error": "Missing shipment_id in path parameters"},
            HTTPStatus.BAD_REQUEST
        )

    try:
        shipment_id = int(shipment_id)
    except ValueError:
        return make_response(
            {"error": "Invalid shipment_id format"},
            HTTPStatus.BAD_REQUEST
        )

    try:
        json_body = json.loads(event.get("body") or "{}")
    except:
        return make_response({"error": "Invalid JSON body"}, HTTPStatus.BAD_REQUEST)

    error_response = _validate_claims(role, user_id, warehouse_id)
    if error_response:
        return error_response

    try:
        update_data = UpdateShipmentRequestSchema().load(json_body)
    except ValidationError as err:
        return make_response({"error": err.messages}, HTTPStatus.BAD_REQUEST)

    try:
        with get_session() as session:
            shipment = session.query(models.Shipment).filter(
                models.Shipment.id == shipment_id
            ).first()

            if not shipment:
                return make_response(
                    {"error": "Shipment not found"},
                    HTTPStatus.NOT_FOUND
                )

            access_error = _validate_shipment_access(session, shipment, role, user_id, warehouse_id)
            if access_error:
                return access_error

            update_result = _apply_updates(session, shipment, update_data, role, user_id)
            if isinstance(update_result, dict) and "error" in update_result:
                return make_response(update_result, HTTPStatus.BAD_REQUEST)

            session.commit()

            logger.info(f"Successfully updated shipment {shipment.id} by user {user_id} with role {role}")

            response_data = {
                "id": shipment.id,
                "status": shipment.status.value,
                "created_at": str(shipment.created_at),
                "in_transit_at": str(shipment.in_transit_at) if shipment.in_transit_at else None,
                "delivered_at": str(shipment.delivered_at) if shipment.delivered_at else None,
                "origin_warehouse_id": shipment.origin_warehouse_id,
                "destination_warehouse_id": shipment.destination_warehouse_id,
                "assigned_carrier_id": shipment.assigned_carrier_id,
                "created_by_id": shipment.created_by_id,
                "in_transit_by_id": shipment.in_transit_by_id,
                "delivered_by_id": shipment.delivered_by_id,
            }

            return make_response(
                UpdateShipmentResponseSchema().dump(response_data),
                HTTPStatus.OK
            )

    except Exception as e:
        logger.error(f"Error updating shipment: {str(e)}", exc_info=True)
        return make_response(
            {"error": "Internal server error"},
            HTTPStatus.INTERNAL_SERVER_ERROR
        )


def _validate_claims(role, user_id, warehouse_id):
    if not user_id:
        return make_response(
            {"error": "Missing user_id in token claims"},
            HTTPStatus.UNAUTHORIZED
        )

    if role == "warehouse_staff" and not warehouse_id:
        return make_response(
            {"error": "Missing warehouse_id in token claims"},
            HTTPStatus.UNAUTHORIZED
        )
    
    return None


def _validate_shipment_access(session, shipment, role, user_id, warehouse_id):
    if role == "warehouse_staff":
        if shipment.origin_warehouse_id != warehouse_id and shipment.destination_warehouse_id != warehouse_id:
            return make_response(
                {"error": "You can only update shipments from your assigned warehouse"},
                HTTPStatus.FORBIDDEN
            )
    
    elif role == "carrier":
        if shipment.assigned_carrier_id != user_id:
            return make_response(
                {"error": "You can only update shipments assigned to you"},
                HTTPStatus.FORBIDDEN
            )
    
    return None


def _apply_updates(session, shipment, update_data, role, user_id):
    status = update_data.get("status")
    location = update_data.get("location")
    
    if role == "warehouse_staff" and status:
        return _handle_status_transition(session, shipment, status, user_id)
    
    elif role == "carrier" and location:
        return _handle_location_update(session, shipment, location)
    
    if not status and not location:
        return {"error": "No valid updates provided"}
    
    if role == "carrier" and status:
        return {"error": "Carriers cannot update shipment status"}
    
    if role == "warehouse_staff" and location:
        return {"error": "Warehouse staff cannot update location"}
    
    return None


def _handle_status_transition(session, shipment, new_status, user_id):
    current_status = shipment.status.value
    new_status_enum = models.ShipmentStatus(new_status)
    
    valid_transitions = {
        "created": ["in_transit"],
        "in_transit": ["delivered"],
        "delivered": []  
    }
    
    if new_status not in valid_transitions.get(current_status, []):
        return {"error": f"Invalid status transition from {current_status} to {new_status}"}
    
    shipment.status = new_status_enum
    
    if new_status == "in_transit":
        shipment.in_transit_at = datetime.now(timezone.utc)
        shipment.in_transit_by_id = user_id
    elif new_status == "delivered":
        shipment.delivered_at = datetime.now(timezone.utc)
        shipment.delivered_by_id = user_id
    
    return None


def _handle_location_update(session, shipment, location):
    if shipment.status != models.ShipmentStatus.in_transit:
        return {"error": "Location can only be updated for shipments in transit"}
    
    new_location = models.ShipmentLocation(
        shipment_id=shipment.id,
        postal_code=location,
        noted_at=datetime.now(timezone.utc)
    )
    session.add(new_location)
    
    return None
