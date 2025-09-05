from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)  # demo only
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    store_id: Mapped[str | None] = mapped_column(String(20))
    carrier_id: Mapped[str | None] = mapped_column(String(20))

class Shipment(Base):
    __tablename__ = "shipments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    origin_store: Mapped[str] = mapped_column(String(20), nullable=False)
    destination_store: Mapped[str] = mapped_column(String(20), nullable=False)
    carrier_id: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="created")
    location: Mapped[str | None] = mapped_column(String(40))
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), onupdate=func.now())