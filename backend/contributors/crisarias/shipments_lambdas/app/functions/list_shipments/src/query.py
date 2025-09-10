from app.common.python.shared.domain.models import Shipment, Warehouse, User, ShipmentLocation, UserRole
from app.common.python.shared.domain.schemas import ShipmentSchema
from app.common.python.shared.infrastructure.database import get_session
from app.common.python.shared.infrastructure.telemetry import logger
from app.common.python.shared.domain.models import Shipment, Warehouse

from sqlalchemy import or_
from sqlalchemy.orm import aliased

def warehouse_dict(name, postal_code):
    return {
        "name": name,
        "postal_code": postal_code
    }

def user_dict(username):
    return {
        "username": username or ''
    }

def location_dict(loc):
    return {
        "postal_code": loc["postal_code"],
        "noted_at": loc["noted_at"].isoformat() if loc["noted_at"] else None
    }


def shipment_list_by_role_and_status(user: User, status: str) -> list[Shipment]:
    session = None
    try:
        session = get_session()
        # Aliases for joins
        target_warehouse = aliased(Warehouse)
        carrier = aliased(User)
        created_by = aliased(User)
        in_transit_by = aliased(User)
        delivered_by = aliased(User)

        # Build base query with all necessary joins and columns
        base_query = session.query(
            Shipment.id,
            Shipment.status,
            Shipment.created_at,
            Shipment.in_transit_at,
            Shipment.delivered_at,
            Warehouse.name.label('origin_warehouse_name'),
            Warehouse.postal_code.label('origin_warehouse_postal_code'),
            target_warehouse.name.label('target_warehouse_name'),
            target_warehouse.postal_code.label('target_warehouse_postal_code'),
            carrier.username.label('carrier_username'),
            created_by.username.label('created_by_username'),
            in_transit_by.username.label('in_transit_by_username'),
            delivered_by.username.label('delivered_by_username'),
        )
        base_query = base_query.join(Warehouse, Shipment.origin_warehouse_id == Warehouse.id)
        base_query = base_query.join(target_warehouse, Shipment.destination_warehouse_id == target_warehouse.id)
        base_query = base_query.join(carrier, Shipment.assigned_carrier_id == carrier.id)
        base_query = base_query.join(created_by, Shipment.created_by_id == created_by.id)
        base_query = base_query.outerjoin(in_transit_by, Shipment.in_transit_by_id == in_transit_by.id)
        base_query = base_query.outerjoin(delivered_by, Shipment.delivered_by_id == delivered_by.id)

        isStoreManager = user.get("role") == UserRole.store_manager
        isGlobalManager = user.get("role") == UserRole.global_manager

        # Role and status logic
        if isGlobalManager:
            if status:
                base_query = base_query.filter(Shipment.status == status)
            rows = base_query.all()
        elif isStoreManager:
            # Assuming Warehouse has store_id and user has store_id
            warehouse_id =  user.get("warehouse_id", "")
            if warehouse_id:
                warehouse_filter = or_(
                    Warehouse.id == warehouse_id,
                    target_warehouse.id == warehouse_id
                )
                base_query = base_query.filter(warehouse_filter)
            if status:
                base_query = base_query.filter(Shipment.status == status)
            rows = base_query.all()
        else:
            # Other roles: return empty or handle as needed
            rows = []

        # Get shipment locations for each shipment
        shipment_ids = [row.id for row in rows]
        locations = session.query(ShipmentLocation.shipment_id, ShipmentLocation.postal_code, ShipmentLocation.noted_at).filter(ShipmentLocation.shipment_id.in_(shipment_ids)).all()
        loc_map = {}
        for loc in locations:
            loc_map.setdefault(loc.shipment_id, []).append({"postal_code": loc.postal_code, "noted_at": loc.noted_at})

        # Build output
        result = []
        # Build output according to schema
        for row in rows:
            result.append({
                "id": row.id,
                "status": row.status.value if hasattr(row.status, 'value') else row.status,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "in_transit_at": row.in_transit_at.isoformat() if row.in_transit_at else None,
                "delivered_at": row.delivered_at.isoformat() if row.delivered_at else None,
                "origin_warehouse": warehouse_dict(row.origin_warehouse_name, row.origin_warehouse_postal_code),
                "target_warehouse": warehouse_dict(row.target_warehouse_name, row.target_warehouse_postal_code),
                "carrier": user_dict(row.carrier_username),
                "created_by": user_dict(row.created_by_username),
                "in_transit_by": user_dict(row.in_transit_by_username),
                "delivered_by": user_dict(row.delivered_by_username),
                "shipment_locations": [location_dict(loc) for loc in loc_map.get(row.id, [])]
            })
        validatedData = [ShipmentSchema().load(item) for item in result]
        return validatedData
    except Exception as e:
        logger.error(f"Error retrieving shipments: {e}")
        raise e
    finally:
        session.close()