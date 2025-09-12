from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)          # global_manager | store_manager | warehouse_staff | carrier
    store_id = Column(String, nullable=True)
    carrier_id = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True)
    origin_store = Column(String, nullable=False)
    destination_store = Column(String, nullable=False)
    carrier_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    location = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())