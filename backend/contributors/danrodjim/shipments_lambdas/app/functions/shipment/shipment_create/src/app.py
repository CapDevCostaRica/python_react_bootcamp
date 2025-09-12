from app.common.python.common.authentication.require_role import require_role
from app.common.python.common.database.models import Shipment, User, UserRole as ur, ShipmentLocation, Warehouse
from app.common.python.common.database.database import get_session
from app.common.python.common.response.make_response import make_response
from ...schema import ShippingCreateRequestSchema
from http import HTTPStatus
from datetime import datetime
import base64
import json

@require_role(ur.warehouse_staff, ur.store_manager)
def handler(event, context):
    try:
        body = event.get("body") or {}

        if event.get("isBase64Enconded"):
            body = base64.b64decode(body).decode()

        json_body = json.loads(body)

        user = event.get("claims")
        user_id = user.get("id")

        body = ShippingCreateRequestSchema().load(json_body)

    except:
        return make_response(
            {"error": "Invalid JSON body"},
            HTTPStatus.BAD_REQUEST
        )
    
    if body.get("origin_warehouse") == body.get("target_warehouse"):
        return make_response(
            {"error": "Origin and destination cannot be the same"},
            HTTPStatus.BAD_REQUEST
        )
    
    with get_session() as session:
        origin_warehouse = session.query(Warehouse).filter_by(id=body.get("origin_warehouse")).first()
        destination_warehouse = session.query(Warehouse).filter_by(id=body.get("target_warehouse")).first()

        if not origin_warehouse or not destination_warehouse:
            return make_response(
                {"error": "Origin and/or destination warehouses does not exist"},
                HTTPStatus.BAD_REQUEST
            )

        user_warehouse = session.query(User.warehouse_id).filter_by(id=user_id).first()
        
        if user_warehouse.warehouse_id != body.get("origin_warehouse"):
            return make_response(
                {"error": "You can only start shipments from your own warehouse"},
                HTTPStatus.BAD_REQUEST
            )

        new_shipment = Shipment(
            origin_warehouse_id = body.get("origin_warehouse"),
            destination_warehouse_id = body.get("target_warehouse"),
            assigned_carrier_id = body.get("carrier"),
            status = body.get("status"),
            created_at = datetime.now(),
            created_by_id = user_id
        )

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