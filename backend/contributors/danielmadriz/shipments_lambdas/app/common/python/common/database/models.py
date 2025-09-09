import enum

import sqlalchemy as sa
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserRole(str, enum.Enum):
    global_manager = "global_manager"
    store_manager = "store_manager"
    warehouse_staff = "warehouse_staff"
    carrier = "carrier"


class ShipmentStatus(str, enum.Enum):
    created = "created"
    in_transit = "in_transit"
    delivered = "delivered"


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    role = Column(Enum(UserRole, name="user_roles", native_enum=True), nullable=False)
    warehouse_id = Column(ForeignKey("warehouses.id"), nullable=True)


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True)
    origin_warehouse_id = Column(ForeignKey("warehouses.id"), nullable=False)
    destination_warehouse_id = Column(ForeignKey("warehouses.id"), nullable=False)
    assigned_carrier_id = Column(ForeignKey("users.id"), nullable=False)
    status = Column(
        Enum(ShipmentStatus, name="shipment_statuses", native_enum=True), nullable=False
    )
    created_at = Column(DateTime, server_default=sa.text("now()"), nullable=False)
    in_transit_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    created_by_id = Column(ForeignKey("users.id"), nullable=False)
    in_transit_by_id = Column(ForeignKey("users.id"), nullable=True)
    delivered_by_id = Column(ForeignKey("users.id"), nullable=True)


class ShipmentLocation(Base):
    __tablename__ = "shipment_locations"

    id = Column(Integer, primary_key=True)
    shipment_id = Column(ForeignKey("shipments.id"), nullable=False)
    postal_code = Column(String, nullable=False)
    noted_at = Column(DateTime, server_default=sa.text("now()"), nullable=False)