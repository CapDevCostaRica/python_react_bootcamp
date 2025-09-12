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
    # Check if warehouses already exist
    existing_warehouses = session.query(Warehouse).all()
    if existing_warehouses:
        print("Warehouses already exist, skipping warehouse seeding.")
        return existing_warehouses
    
    new_warehouses = [
        Warehouse(name=name, postal_code=postal_code)
        for name, postal_code in warehouses
    ]
    session.add_all(new_warehouses)
    session.flush()

    return new_warehouses


def seed_users(session, warehouses):
    # Check if users already exist
    existing_users = session.query(User).all()
    if existing_users:
        print("Users already exist, skipping user seeding.")
        return existing_users
    
    store_managers = [
        User(
            username=f"ManagerAt{warehouse.name}",
            role=UserRole.store_manager,
            warehouse_id=warehouse.id,
        )
        for warehouse in warehouses
    ]
    warehouse_staff = [
        User(
            username=f"StaffAt{warehouse.name}",
            role=UserRole.warehouse_staff,
            warehouse_id=warehouse.id,
        )
        for warehouse in warehouses
    ]
    users = (
        store_managers
        + warehouse_staff
        + [
            User(username="GlobalManager", role=UserRole.global_manager),
            User(username="Carrier1", role=UserRole.carrier),
            User(username="Carrier2", role=UserRole.carrier),
        ]
    )
    session.add_all(users)
    session.flush()

    return users


def seed_shipments(session):
    # Check if shipments already exist
    existing_shipments = session.query(Shipment).all()
    if existing_shipments:
        print("Shipments already exist, skipping shipment seeding.")
        return existing_shipments
    
    warehouses = seed_warehouses(session)
    users = seed_users(session, warehouses)
    carriers = [u for u in users if u.role == UserRole.carrier]

    created = []

    for _ in range(8):
        origin, dest = random.sample(warehouses, 2)
        carrier = random.choice(carriers)
        created_by = (
            session.query(User)
            .filter_by(role=UserRole.warehouse_staff, warehouse_id=origin.id)
            .first()
        )

        shipment = Shipment(
            origin_warehouse_id=origin.id,
            destination_warehouse_id=dest.id,
            assigned_carrier_id=carrier.id,
            status=ShipmentStatus.created,
            created_by_id=created_by.id,
        )
        created.append(shipment)

    session.add_all(created)
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