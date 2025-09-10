from flask import Flask, jsonify, request
from sqlalchemy import cast, func, literal
from sqlalchemy.dialects.postgresql import JSON, aggregate_order_by
from sqlalchemy.orm import aliased
from http import HTTPStatus

from app.common.python.common.database import models
from app.common.python.common.authentication.require_role import require_role
from app.common.python.common.database.database import get_session
from app.common.python.common.authentication.jwt import decode_jwt
from .schema import (
    ErrorSchema,
    ShippingListRequestSchema,
    ShippingListResponseSchema,
)

@require_role("global_manager", "store_manager", "warehouse_staff", "carrier")
def handler(event, context):
    json_body = request.get_json(silent=True) or {}
    body = ShippingListRequestSchema().load(json_body)
    
    auth_header = event.get("headers", {}).get("Authorization", "")
    token = auth_header.split(" ", 1)[1].strip() if auth_header else ""
    user_claims = decode_jwt(token) if token else {}
    user_role = user_claims.get("role", "")
    user_id = user_claims.get("user_id")
    user_warehouse_id = user_claims.get("warehouse_id")

    with get_session() as session:
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
        # I need to add the ShippingLocations to the query below
        origin_warehouse = aliased(models.Warehouse)
        target_warehouse = aliased(models.Warehouse)
        created_by_user = aliased(models.User)
        in_transit_by_user = aliased(models.User)
        delivered_by_user = aliased(models.User)
        carrier = aliased(models.User)

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
                carrier.username.label("carrier_username"),
                created_by_user.username.label("created_by_username"),
                in_transit_by_user.username.label("in_transit_by_username"),
                delivered_by_user.username.label("delivered_by_username"),
                locations_subquery.label("shipment_locations"),
            )
            .select_from(models.Shipment)
            .outerjoin(
                origin_warehouse,
                models.Shipment.origin_warehouse_id == origin_warehouse.id,
            )
            .outerjoin(
                target_warehouse,
                models.Shipment.destination_warehouse_id == target_warehouse.id,
            )
            .outerjoin(carrier, models.Shipment.assigned_carrier_id == carrier.id)
            .outerjoin(
                created_by_user, models.Shipment.created_by_id == created_by_user.id
            )
            .outerjoin(
                in_transit_by_user,
                models.Shipment.in_transit_by_id == in_transit_by_user.id,
            )
            .outerjoin(
                delivered_by_user,
                models.Shipment.delivered_by_id == delivered_by_user.id,
            )
        )
        
        # Apply filters based on user role
        # Global Manager - Can see all shipments (no filter needed)
        if user_role == models.UserRole.store_manager:
            # Store Manager can see shipments related to their warehouse
            query = query.filter(
                (models.Shipment.origin_warehouse_id == user_warehouse_id) |
                (models.Shipment.destination_warehouse_id == user_warehouse_id)
            )
        elif user_role == models.UserRole.warehouse_staff:
            # Warehouse staff can only see shipments for their warehouse
            query = query.filter(
                (models.Shipment.origin_warehouse_id == user_warehouse_id) |
                (models.Shipment.destination_warehouse_id == user_warehouse_id)
            )
        elif user_role == models.UserRole.carrier:
            # Carriers can only see shipments assigned to them
            query = query.filter(models.Shipment.assigned_carrier_id == user_id)

        if status := body.get("status"):
            query = query.filter(
                models.Shipment.status == models.ShipmentStatus(status)
            )

    return {
        "body": ShippingListResponseSchema().dump(
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
        ),
        "statusCode": HTTPStatus.OK,
    }