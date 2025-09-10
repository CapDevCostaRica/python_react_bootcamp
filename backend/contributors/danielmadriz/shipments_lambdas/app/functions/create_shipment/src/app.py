from app.common.python.common.authentication.require_role import require_role
from app.common.python.common.database.database import get_session
from app.common.python.common.database import models
from app.common.python.common.response import make_response
from http import HTTPStatus
from .schema import CreateShipmentRequestSchema, CreateShipmentResponseSchema, ErrorSchema
from marshmallow import ValidationError
from datetime import datetime

import json
import logging

logger = logging.getLogger(__name__)


@require_role("warehouse_staff")
def handler(event, context):
    claims = event.get("claims") or {}
    role = claims.get("role")
    user_id = int(claims.get("sub")) if claims.get("sub") else None
    warehouse_id = int(claims.get("warehouse_id")) if claims.get("warehouse_id") else None

    # Parse and validate request body
    try:
        json_body = json.loads(event.get("body") or "{}")
    except:
        return make_response({"error": "Invalid JSON body"}, HTTPStatus.BAD_REQUEST)

    try:
        schema = CreateShipmentRequestSchema()
        schema.context = {"origin_warehouse_id": warehouse_id}
        shipment_data = schema.load(json_body)
    except ValidationError as err:
        return make_response({"error": err.messages}, HTTPStatus.BAD_REQUEST)

    # Validate user permissions
    error_response = _validate_claims(role, user_id, warehouse_id)
    if error_response:
        return error_response

    try:
        with get_session() as session:
            # Validate that warehouses and carrier exist
            validation_error = _validate_entities(session, shipment_data)
            if validation_error:
                return validation_error

            # Create the shipment
            shipment = models.Shipment(
                origin_warehouse_id=shipment_data["origin_warehouse_id"],
                destination_warehouse_id=shipment_data["destination_warehouse_id"],
                assigned_carrier_id=shipment_data["assigned_carrier_id"],
                status=models.ShipmentStatus.created,
                created_by_id=user_id,
            )

            session.add(shipment)
            session.flush()  # Get the ID

            # Add initial location
            initial_location = models.ShipmentLocation(
                shipment_id=shipment.id,
                postal_code=_get_warehouse_postal_code(session, shipment_data["origin_warehouse_id"]),
                noted_at=datetime.utcnow(),
            )
            session.add(initial_location)
            session.commit()

            logger.info(f"Successfully created shipment {shipment.id} from warehouse {shipment.origin_warehouse_id} to {shipment.destination_warehouse_id}")

            response_data = {
                "id": shipment.id,
                "status": shipment.status.value,
                "created_at": str(shipment.created_at),
                "origin_warehouse_id": shipment.origin_warehouse_id,
                "destination_warehouse_id": shipment.destination_warehouse_id,
                "assigned_carrier_id": shipment.assigned_carrier_id,
                "created_by_id": shipment.created_by_id,
            }

            # Return detailed response (can be simplified if needed)
            return make_response(
                CreateShipmentResponseSchema().dump(response_data),
                HTTPStatus.CREATED
            )
            
            # Alternative simple response (like provided code):
            # return make_response(
            #     {"message": "Shipment created successfully."},
            #     HTTPStatus.CREATED
            # )

    except Exception as e:
        logger.error(f"Error creating shipment: {str(e)}", exc_info=True)
        return make_response(
            {"error": "Internal server error"},
            HTTPStatus.INTERNAL_SERVER_ERROR
        )


def _validate_claims(role, user_id, warehouse_id):
    if not warehouse_id:
        return make_response(
            {"error": "Missing warehouse_id in token claims"},
            HTTPStatus.UNAUTHORIZED
        )
    
    if not user_id:
        return make_response(
            {"error": "Missing user_id in token claims"},
            HTTPStatus.UNAUTHORIZED
        )
    
    return None


def _validate_entities(session, shipment_data):
    # Validate origin warehouse exists
    origin_warehouse = session.query(models.Warehouse).filter(
        models.Warehouse.id == shipment_data["origin_warehouse_id"]
    ).first()
    if not origin_warehouse:
        return make_response(
            {"error": "Origin warehouse not found"},
            HTTPStatus.NOT_FOUND
        )

    # Validate destination warehouse exists
    destination_warehouse = session.query(models.Warehouse).filter(
        models.Warehouse.id == shipment_data["destination_warehouse_id"]
    ).first()
    if not destination_warehouse:
        return make_response(
            {"error": "Destination warehouse not found"},
            HTTPStatus.NOT_FOUND
        )

    # Validate carrier exists and is actually a carrier
    carrier = session.query(models.User).filter(
        models.User.id == shipment_data["assigned_carrier_id"]
    ).first()
    if not carrier:
        return make_response(
            {"error": "Carrier not found"},
            HTTPStatus.NOT_FOUND
        )
    
    if carrier.role != models.UserRole.carrier:
        return make_response(
            {"error": "Assigned user is not a carrier"},
            HTTPStatus.BAD_REQUEST
        )

    return None


def _get_warehouse_postal_code(session, warehouse_id):
    warehouse = session.query(models.Warehouse).filter(
        models.Warehouse.id == warehouse_id
    ).first()
    return warehouse.postal_code if warehouse else "00000"
