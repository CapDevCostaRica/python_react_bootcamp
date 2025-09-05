from flask import request
from app.common.python.common.decorators.require_role import require_role
from app.common.python.common.response.response import send_response
from app.common.python.common.database.models import Shipment, ShipmentStatus, UserRole
from app.common.python.common.schema.shipping import CreateShipmentSchema
from app.common.python.common.database.database import get_session
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError

@require_role([UserRole.store_manager, UserRole.warehouse_staff])
def handler(event, context):
    json_body = request.get_json(silent=True) or {}
    user_data = event.get("user_data")

    if not user_data:
        return send_response({ "error": "Invalid token" }, HTTPStatus.UNAUTHORIZED)

    try:
        body = CreateShipmentSchema().load(json_body)
    except Exception as e:
        return send_response({ "error": str(e) }, HTTPStatus.UNAUTHORIZED)

    logged_user_id = user_data.get("id", 0)
    logged_user_warehouse = user_data.get("warehouse_id", 0)
    destination_warehouse_id = body.get("target_warehouse", None)

    if logged_user_warehouse == destination_warehouse_id:
        return send_response({ "error": "Could not create a shipment to the same origin and target" }, HTTPStatus.FORBIDDEN)

    try:
        with get_session() as db:
            carrier = body.get("carrier", None)
            
            new_shipment = Shipment(
                origin_warehouse_id=logged_user_warehouse,
                destination_warehouse_id=destination_warehouse_id,
                status=ShipmentStatus.created,
                created_by_id=logged_user_id,
                assigned_carrier_id = carrier
            )
            
            db.add(new_shipment)
            db.commit()

            return send_response({"insert": "ok"}, HTTPStatus.CREATED)
    except IntegrityError as e:
        db.rollback()
        msg = str(e.orig)  # mensaje de la base de datos
        if "destination_warehouse_id" in msg:
            return send_response({"error": "Invalid warehouse destination"}, HTTPStatus.FORBIDDEN)
        elif "assigned_carrier_id" in msg:
            return send_response({"error": "Invalid carrier"}, HTTPStatus.FORBIDDEN)
        else:
            return send_response({"error": msg}, HTTPStatus.FORBIDDEN)

    except Exception as e:
        return send_response({ "error": str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR)
