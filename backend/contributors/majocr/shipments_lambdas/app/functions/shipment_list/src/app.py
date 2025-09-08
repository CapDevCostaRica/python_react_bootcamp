import datetime
import json
from http import HTTPStatus
from marshmallow import ValidationError
from sqlalchemy import cast, func, literal
from sqlalchemy.dialects.postgresql import JSON, aggregate_order_by
from sqlalchemy.orm import aliased

from app.common.python.common.authentication.require_role_decorator import require_role
from app.common.python.common.database.database import get_session
from app.common.python.common.database import models
from app.common.python.common.response.make_response import make_response
from app.common.python.common.schema.schema import ShippingListRequestSchema, ShippingListResponseSchema

@require_role("global_manager", "store_manager", "warehouse_staff", "carrier")
def handler(event, context):
    claims = event.get("claims") or {}
    role = claims.get("role")
    user_id = claims.get("sub")
    warehouse_id = claims.get("warehouse_id")

    try:
        json_body = json.loads(event.get("body") or "{}")
    except:
        return make_response({"error": "Invalid JSON body"}, HTTPStatus.BAD_REQUEST)

    try:
        filters = ShippingListRequestSchema().load(json_body)
    except ValidationError as err:
        return make_response({"error": err.messages}, HTTPStatus.BAD_REQUEST)

    status_filter = filters.get("status")
    shipment_id = filters.get("id")
    carrier_filter = filters.get("carrier")
    date_range = filters.get("date", {})
    start_date = date_range.get("from_date")
    end_date = date_range.get("to_date")

    with get_session() as session:
        origin_warehouse = aliased(models.Warehouse)
        target_warehouse = aliased(models.Warehouse)
        created_by_user = aliased(models.User)
        in_transit_by_user = aliased(models.User)
        delivered_by_user = aliased(models.User)
        carrier_user = aliased(models.User)

        locations_subquery = (
            session.query(
                func.coalesce(
                    func.json_agg(
                        aggregate_order_by(
                            func.json_build_object(
                                "postal_code", 
                                models.ShipmentLocation.postal_code,
                                "noted_at", 
                                models.ShipmentLocation.noted_at,
                            ),
                            models.ShipmentLocation.noted_at.asc(),
                        )
                    ),
                    cast(literal("[]"), JSON),
                )
            )
            .filter(models.ShipmentLocation.shipment_id == models.Shipment.id)
            .correlate(models.Shipment)
            .scalar_subquery()
        )

        query = (
            session.query(
                models.Shipment.id,
                models.Shipment.status,
                models.Shipment.created_at,
                models.Shipment.in_transit_at,
                models.Shipment.delivered_at,
                origin_warehouse.name.label("origin_warehouse_name"),
                origin_warehouse.postal_code.label("origin_warehouse_postal_code"),
                target_warehouse.name.label("target_warehouse_name"),
                target_warehouse.postal_code.label("target_warehouse_postal_code"),
                carrier_user.username.label("carrier_username"),
                created_by_user.username.label("created_by_username"),
                in_transit_by_user.username.label("in_transit_by_username"),
                delivered_by_user.username.label("delivered_by_username"),
                locations_subquery.label("shipment_locations"),
            )
            .select_from(models.Shipment)
            .outerjoin(origin_warehouse, models.Shipment.origin_warehouse_id == origin_warehouse.id)
            .outerjoin(target_warehouse, models.Shipment.destination_warehouse_id == target_warehouse.id)
            .outerjoin(carrier_user, models.Shipment.assigned_carrier_id == carrier_user.id)
            .outerjoin(created_by_user, models.Shipment.created_by_id == created_by_user.id)
            .outerjoin(in_transit_by_user, models.Shipment.in_transit_by_id == in_transit_by_user.id)
            .outerjoin(delivered_by_user, models.Shipment.delivered_by_id == delivered_by_user.id)
        )

        if role in ("store_manager", "warehouse_staff"):
            query = query.filter(
                (models.Shipment.origin_warehouse_id == warehouse_id) |
                (models.Shipment.destination_warehouse_id == warehouse_id)
            )
        elif role == "carrier":
            query = query.filter(models.Shipment.assigned_carrier_id == user_id)

        if status_filter:
            query = query.filter(models.Shipment.status == status_filter)
        if shipment_id:
            query = query.filter(models.Shipment.id == shipment_id)
        if carrier_filter:
            query = query.filter(models.Shipment.assigned_carrier_id == carrier_filter)
        if start_date and end_date:
            query = query.filter(models.Shipment.created_at.between(start_date, end_date))
        elif start_date:
            query = query.filter(models.Shipment.created_at >= start_date)
        elif end_date:
            query = query.filter(models.Shipment.created_at <= end_date)


        results = []
        for row in query.all():
            results.append({
                "id": row.id,
                "status": row.status,
                "created_at": row.created_at.isoformat(),
                "in_transit_at": row.in_transit_at.isoformat() if row.in_transit_at else None,
                "delivered_at": row.delivered_at.isoformat() if row.delivered_at else None,
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
            })

        response_data = {
            "results": results,
            "result_count": len(results),
        }

        return make_response(
            ShippingListResponseSchema().dump(response_data),
            HTTPStatus.OK
        )
