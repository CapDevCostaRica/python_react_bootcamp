from sqlalchemy import cast, func, literal, or_, and_
from sqlalchemy.dialects.postgresql import JSON, aggregate_order_by
from sqlalchemy.orm import aliased
from app.common.python.common.authentication.require_role import require_role
from app.common.python.common.database.models import User, Shipment, ShipmentLocation, ShipmentStatus, Warehouse, UserRole as ur
from app.common.python.common.database.database import get_session
from app.common.python.common.response.make_response import make_response
from ...schema import ShippingListRequestSchema, ShippingListResponseSchema
from app.common.python.common.authentication.jwt import decode_jwt
from http import HTTPStatus
import base64
import json

@require_role(ur.global_manager, ur.store_manager, ur.warehouse_staff, ur.carrier)
def handler(event, context):
    try:
        body = event.get("body") or {}

        if event.get("isBase64Enconded"):
            body = base64.b64decode(body).decode()

        json_body = json.loads(body)

        body = ShippingListRequestSchema().load(json_body)
    except:
        return make_response(
            {"error": "Invalid JSON body"},
            HTTPStatus.BAD_REQUEST
        )

    user = event.get("claims")
    role = user.get("role")

    with get_session() as session:
        locations_subquery = (
            session.query(
                func.coalesce(
                    func.json_agg(
                        aggregate_order_by(
                            func.json_build_object(
                                "postal_code",
                                ShipmentLocation.postal_code,
                                "noted_at",
                                ShipmentLocation.noted_at,
                            ),
                            ShipmentLocation.noted_at.asc(),
                        )
                    ),
                    cast(literal("[]"), JSON),
                )
            )
            .filter(ShipmentLocation.shipment_id == Shipment.id)
            .correlate(Shipment)
            .scalar_subquery()
        )

        origin_warehouse = aliased(Warehouse)
        target_warehouse = aliased(Warehouse)
        created_by_user = aliased(User)
        in_transit_by_user = aliased(User)
        delivered_by_user = aliased(User)
        carrier = aliased(User)

        query = (
            session.query(
                Shipment.id,
                Shipment.status,
                Shipment.created_at,
                Shipment.in_transit_at,
                Shipment.delivered_at,
                origin_warehouse.name.label("origin_warehouse_name"),
                origin_warehouse.postal_code.label("origin_warehouse_postal_code"),
                target_warehouse.name.label("target_warehouse_name"),
                target_warehouse.postal_code.label("target_warehouse_postal_code"),
                carrier.username.label("carrier_username"),
                created_by_user.username.label("created_by_username"),
                in_transit_by_user.username.label("in_transit_by_username"),
                delivered_by_user.username.label("delivered_by_username"),
                locations_subquery.label("shipment_locations"),
            )
            .select_from(Shipment)
            .outerjoin(
                origin_warehouse,
                Shipment.origin_warehouse_id == origin_warehouse.id,
            )
            .outerjoin(
                target_warehouse,
                Shipment.destination_warehouse_id == target_warehouse.id,
            )
            .outerjoin(
                carrier, 
                Shipment.assigned_carrier_id == carrier.id)
            .outerjoin(
                created_by_user, 
                Shipment.created_by_id == created_by_user.id
            )
            .outerjoin(
                in_transit_by_user,
                Shipment.in_transit_by_id == in_transit_by_user.id,
            )
            .outerjoin(
                delivered_by_user,
                Shipment.delivered_by_id == delivered_by_user.id,
            )
        )

        date = body.get("date")
        if date:
            query = query.filter(
                or_(
                    and_(
                        func.date(Shipment.created_at) <= date,
                        func.date(Shipment.delivered_at) >= date
                    ),
                    and_(
                        func.date(Shipment.created_at) <= date,
                        func.date(Shipment.in_transit_at) >= date
                    ),
                    and_(
                        func.date(Shipment.created_at) == date,
                        Shipment.delivered_at == None,
                        Shipment.in_transit_at == None
                    )
                )
            )

        shipment_id = body.get("id")
        if shipment_id:
            query = query.filter(
                Shipment.id == shipment_id
            )

        status = body.get("status")
        if status:
            query = query.filter(
                Shipment.status == ShipmentStatus(status)
            )

        carrier = body.get("carrier")
        if carrier:
            query = query.filter(
                or_(
                    Shipment.assigned_carrier_id == carrier,
                    Shipment.in_transit_by_id == carrier,
                    Shipment.delivered_by_id == carrier
                )
            )

        if role == ur.store_manager or role == ur.warehouse_staff:
            query = query.filter(
                or_(
                    Shipment.origin_warehouse_id == user.get("warehouse_id"),
                    Shipment.destination_warehouse_id == user.get("warehouse_id")
                )
            )
        elif role == ur.carrier:
            query = query.filter(
                Shipment.assigned_carrier_id == user.get("id")
            )

        shipping_list = ShippingListResponseSchema().dump(
            {
                "results": [
                    {
                        "id": row.id,
                        "status": row.status,
                        "created_at": row.created_at,
                        "in_transit_at": row.in_transit_at,
                        "delivered_at": row.delivered_at,
                        "origin_warehouse": {
                            "name": row.origin_warehouse_name,
                            "postal_code": row.origin_warehouse_postal_code,
                        },
                        "target_warehouse": {
                            "name": row.target_warehouse_name,
                            "postal_code": row.target_warehouse_postal_code,
                        },
                        "carrier": {"username": row.carrier_username},
                        "created_by": {"username": row.created_by_username},
                        "in_transit_by": {"username": row.in_transit_by_username},
                        "delivered_by": {"username": row.delivered_by_username},
                        "shipment_locations": row.shipment_locations,
                    }
                    for row in query.all()
                ],
                "result_count": query.count(),
            }
        )

        return make_response(
            {"Shipping List": shipping_list},
            HTTPStatus.OK
        )
