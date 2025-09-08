import json
from http import HTTPStatus
from datetime import datetime
from marshmallow import ValidationError

from app.common.python.common.authentication.require_role_decorator import require_role
from app.common.python.common.response.make_response import make_response
from app.common.python.common.database.database import get_session
from app.common.python.common.database import models
from app.common.python.common.schema.schema import ShipmentCreateRequestSchema



@require_role("warehouse_staff")
def handler(event, context):
    claims = event.get("claims") or {}
    user_id = claims.get("sub")
    print("Claims:", claims)
    print("User ID:", user_id)
    warehouse_id = claims.get("warehouse_id")
    
    if not user_id:
        return make_response({"error": "Missing user identity in token."}, HTTPStatus.UNAUTHORIZED)

    try:
        json_body = json.loads(event.get("body") or "{}")
    except:
        return make_response({"error": "Invalid JSON body"}, HTTPStatus.BAD_REQUEST)
    
    try:
        schema = ShipmentCreateRequestSchema()
        schema.context = {"origin_warehouse_id": warehouse_id}
        payload = schema.load(json_body)
    except ValidationError as err:
        return make_response({"error": err.messages}, HTTPStatus.BAD_REQUEST)
      
    new_shipment = models.Shipment(
        origin_warehouse_id = payload["origin_warehouse_id"],
        destination_warehouse_id = payload["destination_warehouse_id"],
        assigned_carrier_id = payload["assigned_carrier_id"],
        status = "created",
        created_by_id = user_id,
        created_at = datetime.utcnow()
    )

    with get_session() as session:
        carrier = session.query(models.User).get(payload["assigned_carrier_id"])
        if not carrier or carrier.role != "carrier":
            return make_response({"error": "Assigned carrier is invalid."}, HTTPStatus.BAD_REQUEST)

        session.add(new_shipment)
        session.commit()

    return make_response(
        {
            "message": "Shipment created successfully."
        },
        HTTPStatus.CREATED
    )


 