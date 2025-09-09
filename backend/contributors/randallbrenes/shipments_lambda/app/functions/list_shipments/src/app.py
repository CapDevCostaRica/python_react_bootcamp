from flask import request
from app.common.python.common.decorators.require_role import require_role
from app.common.python.common.response.response import send_response
from app.common.python.common.database.models import Warehouse, User, Shipment, ShipmentLocation, ShipmentStatus, UserRole
from app.common.python.common.schema.shipping import ShippingListRequestSchema, ShippingListResponseSchema
from app.common.python.common.database.database import get_session
from http import HTTPStatus
from sqlalchemy import and_, or_, cast, func, literal, true
from sqlalchemy.dialects.postgresql import JSON, aggregate_order_by
from sqlalchemy.orm import aliased


def base_query(session):
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
        session.query (
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
        .outerjoin(carrier, Shipment.assigned_carrier_id == carrier.id)
        .outerjoin(
            created_by_user, Shipment.created_by_id == created_by_user.id
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
    return query

@require_role(["global_manager", "store_manager", "warehouse_staff", "carrier"])
def handler(event, context):
    json_body = request.get_json(silent=True) or {}
    user_data = event.get("user_data")

    if not user_data:
        return send_response({ "error": "Invalid token" }, HTTPStatus.UNAUTHORIZED)

    try:
        body = ShippingListRequestSchema().load(json_body)

    except Exception as e:
        return send_response({ "error": str(e) }, HTTPStatus.BAD_REQUEST)

    role = user_data.get("role", "")
    logged_user_id = user_data.get("id", 0)
    logged_user_warehouse = user_data.get("warehouse_id", 0)

    list_response = {
        "result_count": 0,
        "results": []
    }
    with get_session() as db:
        query = base_query(db)
        filters = []
        if status := body.get("status"):
            filters.append(Shipment.status == ShipmentStatus(status))

        if date := body.get("date"):
            start = date.get("from_date")
            end = date.get("to_date")
            if start:
                filters.append(Shipment.created_at >= start)
            if end:
                filters.append(Shipment.created_at <= end)

        if carrier := body.get("carrier"):
            filters.append(Shipment.assigned_carrier_id == int(carrier))

        if filter_id := body.get("id"):
            filters.append(Shipment.id == filter_id)

        if role == UserRole.carrier:
            # 10. A Carrier can view shipments assigned to them
            filters.append(Shipment.assigned_carrier_id == logged_user_id)
        elif role == UserRole.warehouse_staff:
            # 9. A Warehouse Staff can view shipments where their warehouse is either the origin or destination
            filters.append(or_(Shipment.origin_warehouse_id == logged_user_warehouse, Shipment.destination_warehouse_id == logged_user_warehouse))
        elif role == UserRole.store_manager:
            # 8. A Store Manager   can view shipments where their store     is either the origin or destination
            filters.append(or_(Shipment.origin_warehouse_id == logged_user_warehouse, Shipment.destination_warehouse_id == logged_user_warehouse))
        elif role == UserRole.global_manager:
            # A Global Manager can view all shipments across the state
            pass
        else:
            return send_response({ "error": "Invalid role" }, HTTPStatus.FORBIDDEN)

        query = query.where(and_(true(), *filters))
        list_response["results"] = [
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
                    ]
        list_response["result_count"] = query.count()
    
    try:
        response = ShippingListResponseSchema().dump(list_response)

    except Exception as err:
        return send_response({ "error": "Invalid response" }, HTTPStatus.INTERNAL_SERVER_ERROR)
    return send_response(response, HTTPStatus.OK)
