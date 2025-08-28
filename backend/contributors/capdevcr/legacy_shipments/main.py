import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../framework"))
)

from http import HTTPStatus

import models
from auth import JWTError, decode_jwt, encode_jwt
from database import get_session
from flask import Flask, jsonify, request
from schemas import (
    ErrorSchema,
    LoginRequestSchema,
    LoginResponseSchema,
    ShippingListRequestSchema,
)
from sqlalchemy import cast, func, literal
from sqlalchemy.dialects.postgresql import JSON, aggregate_order_by
from sqlalchemy.orm import aliased

app = Flask(__name__)

USERS = {
    "manager": {"sub": "manager", "role": "manager"},
    "warehouse_dependent": {
        "sub": "warehouse_dependent",
        "role": "warehouse_dependent",
    },
}


@app.post("/login")
def login():
    json_body = request.get_json(silent=True) or {}
    body = LoginRequestSchema().load(json_body)
    username = body.get("username")
    user = USERS.get(username)

    if not user:
        return jsonify(
            ErrorSchema().dump({"error": "Invalid username"})
        ), HTTPStatus.NOT_FOUND

    token = encode_jwt(user)

    return jsonify(
        LoginResponseSchema().dump({"access_token": token, "token_type": "Bearer"})
    ), HTTPStatus.OK


@app.post("/shipment/list")
def list_shipments():
    expected_roles = ("manager", "warehouse_dependent")
    auth = request.headers.get("Authorization", "")

    if not auth.startswith("Bearer "):
        return jsonify(
            ErrorSchema().dump({"error": "Unauthorized"})
        ), HTTPStatus.UNAUTHORIZED

    try:
        claims = decode_jwt(auth.split(" ", 1)[1].strip())

    except JWTError as e:
        return jsonify(ErrorSchema().dump({"error": str(e)})), HTTPStatus.UNAUTHORIZED

    if claims.get("role") not in expected_roles:
        return jsonify(ErrorSchema().dump({"error": "Forbidden"})), HTTPStatus.FORBIDDEN

    json_body = request.get_json(silent=True) or {}
    body = ShippingListRequestSchema().load(json_body)

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

        if status := body.get("status"):
            query = query.filter(
                models.Shipment.status == models.ShipmentStatus(status)
            )

        return {
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
