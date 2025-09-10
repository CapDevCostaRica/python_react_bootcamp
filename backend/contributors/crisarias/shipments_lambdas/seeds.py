import random
from datetime import timedelta

from app.database import get_session
from app.models import (
    Shipment,
    ShipmentLocation,
    ShipmentStatus,
    User,
    UserRole,
    Warehouse,
)

warehouses = [
    ("San Francisco Warehouse", "94103"),
    ("Los Angeles Warehouse", "90001"),
    ("San Diego Warehouse", "92101"),
    ("Sacramento Warehouse", "95814"),
]


def seed_warehouses(session):
    existing = {w.name: w for w in session.query(Warehouse).all()}
    new_warehouses = []
    for name, postal_code in warehouses:
        if name not in existing:
            warehouse = Warehouse(name=name, postal_code=postal_code)
            session.add(warehouse)
            new_warehouses.append(warehouse)
        else:
            new_warehouses.append(existing[name])
    session.flush()
    return new_warehouses


def seed_users(session, warehouses):
    existing = {u.username: u for u in session.query(User).all()}
    users = []
    # Store managers
    for warehouse in warehouses:
        username = f"ManagerAt{warehouse.name}"
        if username not in existing:
            user = User(username=username, role=UserRole.store_manager, warehouse_id=warehouse.id)
            session.add(user)
            users.append(user)
        else:
            users.append(existing[username])
    # Warehouse staff
    for warehouse in warehouses:
        username = f"StaffAt{warehouse.name}"
        if username not in existing:
            user = User(username=username, role=UserRole.warehouse_staff, warehouse_id=warehouse.id)
            session.add(user)
            users.append(user)
        else:
            users.append(existing[username])
    # GlobalManager and Carriers
    for username, role in [("GlobalManager", UserRole.global_manager), ("Carrier1", UserRole.carrier), ("Carrier2", UserRole.carrier)]:
        if username not in existing:
            user = User(username=username, role=role)
            session.add(user)
            users.append(user)
        else:
            users.append(existing[username])
    session.flush()
    return users


def seed_shipments(session):
    warehouses = seed_warehouses(session)
    users = seed_users(session, warehouses)
    carriers = [u for u in users if u.role == UserRole.carrier]

    created = []
    existing_shipments = {(s.origin_warehouse_id, s.destination_warehouse_id, s.assigned_carrier_id): s for s in session.query(Shipment).all()}

    for _ in range(8):
        origin, dest = random.sample(warehouses, 2)
        carrier = random.choice(carriers)
        created_by = (
            session.query(User)
            .filter_by(role=UserRole.warehouse_staff, warehouse_id=origin.id)
            .first()
        )
        key = (origin.id, dest.id, carrier.id)
        if key not in existing_shipments:
            shipment = Shipment(
                origin_warehouse_id=origin.id,
                destination_warehouse_id=dest.id,
                assigned_carrier_id=carrier.id,
                status=ShipmentStatus.created,
                created_by_id=created_by.id,
            )
            created.append(shipment)
            session.add(shipment)
        else:
            created.append(existing_shipments[key])
    session.flush()

    # Promote some shipments to in_transit / delivered and add location history
    zips = ["94103", "94016", "90045", "90001", "92101", "95814", "95014", "95134"]

    for shipment in created:
        # Add at least one location at creation
        session.add(
            ShipmentLocation(
                shipment_id=shipment.id,
                postal_code=random.choice(zips),
                noted_at=shipment.created_at + timedelta(hours=1),
            )
        )

        if random.random() < 0.6:
            shipment.status = ShipmentStatus.in_transit
            shipment.in_transit_at = shipment.created_at + timedelta(hours=2)
            shipment.in_transit_by_id = shipment.created_by_id
            session.add(
                ShipmentLocation(
                    shipment_id=shipment.id,
                    postal_code=random.choice(zips),
                    noted_at=shipment.in_transit_at + timedelta(hours=1),
                )
            )

        if shipment.status == ShipmentStatus.in_transit and random.random() < 0.5:
            staff_member = (
                session.query(User)
                .filter_by(
                    role=UserRole.warehouse_staff,
                    warehouse_id=shipment.destination_warehouse_id,
                )
                .first()
            )
            shipment.status = ShipmentStatus.delivered
            shipment.delivered_at = shipment.in_transit_at + timedelta(hours=6)
            shipment.delivered_by_id = staff_member.id
            session.add(
                ShipmentLocation(
                    shipment_id=shipment.id,
                    postal_code=random.choice(zips),
                    noted_at=shipment.delivered_at - timedelta(hours=1),
                )
            )

    session.commit()

    print("Seeded warehouses, users, and shipments.")
    print(
        f"Created {len(warehouses)} warehouses, {len(users)} users, and {len(created)} shipments."
    )

    return created


if __name__ == "__main__":
    session = get_session()
    shipments = seed_shipments(session)
    session.close()
