from app.common.python.common.authentication.require_role import require_role
from app.common.python.common.database.database import get_session
from app.common.python.common.database import models
from app.common.python.common.response import make_response
from http import HTTPStatus
from .schema import ShippingListRequestSchema, ShippingListResponseSchema, ErrorSchema
from sqlalchemy import func, cast, literal, JSON
from sqlalchemy.orm import aliased
from sqlalchemy.dialects.postgresql import aggregate_order_by
from marshmallow import ValidationError

import json


@require_role("global_manager", "store_manager", "warehouse_staff", "carrier")
def handler(event, context):
    claims = event.get("claims") or {}
    role = claims.get("role")
    user_id = int(claims.get("sub")) if claims.get("sub") else None
    warehouse_id = int(claims.get("warehouse_id")) if claims.get("warehouse_id") else None

    print(f"🔍 HANDLER DEBUG: claims={claims}")
    print(f"🔍 HANDLER DEBUG: role={role}, user_id={user_id}, warehouse_id={warehouse_id}")

    filters, error_response = _parse_request_body(event)
    if error_response:
        return error_response

    error_response = _validate_claims(role, user_id, warehouse_id)
    if error_response:
        return error_response

    try:
        with get_session() as session:
            
            locations_subquery = _build_locations_subquery(session)
            query = _build_base_query(session, locations_subquery)
            
            query, filters_applied = _apply_filters(query, role, user_id, warehouse_id, filters)
            
            count_query = session.query(func.count(models.Shipment.id))
            if filters_applied:
                count_query = count_query.filter(*filters_applied)
            total_count = count_query.scalar()
            query_results = query.all()
            
            results = _format_results(query_results)

            response_data = {
                "results": results,
                "result_count": total_count,
            }

            return make_response(
                ShippingListResponseSchema().dump(response_data),
                HTTPStatus.OK
            )

    except Exception as e:
        return make_response(
            {"error": "Internal server error"},
            HTTPStatus.INTERNAL_SERVER_ERROR
        )


def _parse_request_body(event):
    try:
        json_body = json.loads(event.get("body") or "{}")
    except:
        return None, make_response({"error": "Invalid JSON body"}, HTTPStatus.BAD_REQUEST)

    try:
        filters = ShippingListRequestSchema().load(json_body)
        return filters, None
    except ValidationError as err:
        return None, make_response({"error": err.messages}, HTTPStatus.BAD_REQUEST)


def _validate_claims(role, user_id, warehouse_id):
    if role in ("store_manager", "warehouse_staff") and not warehouse_id:
        return make_response(
            {"error": "Missing warehouse_id in token claims"},
            HTTPStatus.UNAUTHORIZED
        )
    
    if role == "carrier" and not user_id:
        return make_response(
            {"error": "Missing user_id in token claims"},
            HTTPStatus.UNAUTHORIZED
        )
    
    return None


def _build_locations_subquery(session):
    return (
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


def _build_base_query(session, locations_subquery):
    origin_warehouse = aliased(models.Warehouse)
    target_warehouse = aliased(models.Warehouse)
    created_by_user = aliased(models.User)
    in_transit_by_user = aliased(models.User)
    delivered_by_user = aliased(models.User)
    carrier_user = aliased(models.User)

    return (
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


def _apply_filters(query, role, user_id, warehouse_id, filters):
    filters_applied = []
    
    print(f"🔍 FILTER DEBUG: role={role}, user_id={user_id}, warehouse_id={warehouse_id}")
    print(f"🔍 FILTER DEBUG: filters={filters}")
    
    if role in ("store_manager", "warehouse_staff"):
        print(f"🔍 FILTER DEBUG: Applying store_manager/warehouse_staff filter for warehouse_id={warehouse_id}")
        filters_applied.append(
            (models.Shipment.origin_warehouse_id == warehouse_id) |
            (models.Shipment.destination_warehouse_id == warehouse_id)
        )
    elif role == "carrier":
        print(f"🔍 FILTER DEBUG: Applying carrier role filter for user_id={user_id}")
        filters_applied.append(models.Shipment.assigned_carrier_id == user_id)

    status_filter = filters.get("status")
    shipment_id = filters.get("id")
    carrier_filter = filters.get("carrier")
    date_range = filters.get("date", {})
    start_date = date_range.get("from_date")
    end_date = date_range.get("to_date")

    if status_filter:
        print(f"🔍 FILTER DEBUG: Applying status filter: {status_filter}")
        filters_applied.append(models.Shipment.status == status_filter)
    if shipment_id:
        print(f"🔍 FILTER DEBUG: Applying shipment_id filter: {shipment_id}")
        filters_applied.append(models.Shipment.id == shipment_id)
    if carrier_filter and role != "carrier":  # Only apply carrier filter if user is not a carrier
        print(f"🔍 FILTER DEBUG: Applying carrier filter: {carrier_filter} (user is not a carrier)")
        filters_applied.append(models.Shipment.assigned_carrier_id == carrier_filter)
    elif carrier_filter and role == "carrier":
        print(f"🔍 FILTER DEBUG: Ignoring carrier filter: {carrier_filter} (user is a carrier, using role-based filter instead)")
    if start_date and end_date:
        print(f"🔍 FILTER DEBUG: Applying date range filter: {start_date} to {end_date}")
        filters_applied.append(models.Shipment.created_at.between(start_date, end_date))
    elif start_date:
        print(f"🔍 FILTER DEBUG: Applying start_date filter: {start_date}")
        filters_applied.append(models.Shipment.created_at >= start_date)
    elif end_date:
        print(f"🔍 FILTER DEBUG: Applying end_date filter: {end_date}")
        filters_applied.append(models.Shipment.created_at <= end_date)
    
    print(f"🔍 FILTER DEBUG: Total filters applied: {len(filters_applied)}")
    if filters_applied:
        query = query.filter(*filters_applied)
    
    return query, filters_applied




def _format_results(query_results):
    results = []
    for row in query_results:
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
    return results