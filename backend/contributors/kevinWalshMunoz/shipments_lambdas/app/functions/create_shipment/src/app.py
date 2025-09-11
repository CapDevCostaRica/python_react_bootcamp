from flask import Flask, jsonify, request
from http import HTTPStatus
from datetime import datetime
import sqlalchemy as sa
from marshmallow import ValidationError

from app.common.python.common.database import models
from app.common.python.common.authentication.require_role import require_role
from app.common.python.common.database.database import get_session
from app.common.python.common.authentication.jwt import decode_jwt
from .schema import (
    ErrorSchema,
    CreateShipmentRequestSchema,
    CreateShipmentResponseSchema,
)


@require_role("global_manager", "store_manager", "warehouse_staff")
def handler(event, context):
    # Parse and validate request body
    json_body = request.get_json(silent=True) or {}
    try:
        body = CreateShipmentRequestSchema().load(json_body)
    except ValidationError as e:
        return {
            "body": ErrorSchema().dump({"error": str(e)}),
            "statusCode": HTTPStatus.BAD_REQUEST,
        }
    
    # Extract user info from JWT
    auth_header = event.get("headers", {}).get("Authorization", "")
    token = auth_header.split(" ", 1)[1].strip() if auth_header else ""
    user_claims = decode_jwt(token) if token else {}
    user_id = user_claims.get("user_id")
    
    with get_session() as session:
        origin_warehouse = session.query(models.Warehouse).get(body["origin_warehouse_id"])
        if not origin_warehouse:
            return {
                "body": ErrorSchema().dump({"error": "Origin warehouse does not exist"}),
                "statusCode": HTTPStatus.BAD_REQUEST,
            }
        
        destination_warehouse = session.query(models.Warehouse).get(body["destination_warehouse_id"])
        if not destination_warehouse:
            return {
                "body": ErrorSchema().dump({"error": "Destination warehouse does not exist"}),
                "statusCode": HTTPStatus.BAD_REQUEST,
            }
        
        carrier = session.query(models.User).get(body["assigned_carrier_id"])
        if not carrier:
            return {
                "body": ErrorSchema().dump({"error": "Assigned carrier does not exist"}),
                "statusCode": HTTPStatus.BAD_REQUEST,
            }
        
        if carrier.role != models.UserRole.carrier:
            return {
                "body": ErrorSchema().dump({"error": "Assigned user must have carrier role"}),
                "statusCode": HTTPStatus.BAD_REQUEST,
            }
        
        # Create the shipment
        shipment = models.Shipment(
            origin_warehouse_id=body["origin_warehouse_id"],
            destination_warehouse_id=body["destination_warehouse_id"],
            assigned_carrier_id=body["assigned_carrier_id"],
            status=models.ShipmentStatus.created,
            created_by_id=user_id,
            created_at=datetime.now()
        )
        
        session.add(shipment)
        session.commit()
        
        # Create response
        response = {
            "id": shipment.id,
            "status": shipment.status,
            "created_at": shipment.created_at.isoformat(),
            "origin_warehouse_id": shipment.origin_warehouse_id,
            "destination_warehouse_id": shipment.destination_warehouse_id,
            "assigned_carrier_id": shipment.assigned_carrier_id,
            "created_by_id": shipment.created_by_id,
        }
        
        return {
            "body": CreateShipmentResponseSchema().dump(response),
            "statusCode": HTTPStatus.CREATED,
        }
