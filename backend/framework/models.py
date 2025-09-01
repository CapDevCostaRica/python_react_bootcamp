import enum
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
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


class MotivationalPhrase(Base):
    __tablename__ = "motivational_phrases"
    id = Column(Integer, primary_key=True)
    phrase = Column(String)


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


# Monster cache for randymorales proxy
class randymorales_MonsterCache(Base):
    __tablename__ = "randymorales_monster_cache"
    id = Column(Integer, primary_key=True)
    monster_index = Column(String, unique=True, nullable=False)
    monster_data = Column(String, nullable=False)  # Store JSON as string


class randymorales_MonsterListCache(Base):
    __tablename__ = "randymorales_monster_list_cache"
    id = Column(Integer, primary_key=True)
    resource = Column(String, unique=True, nullable=False)
    list_data = Column(String, nullable=False)  # Store JSON as string


class kevinWalshMunozMonsterList(Base):
    __tablename__ = "kevinWalshMunozMonsters"

    index = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)


class kevinWalshMunozMonster(Base):
    __tablename__ = "kevinWalshMunozMonster"

    id = Column(Integer, primary_key=True)
    index = Column(Text, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    size = Column(Text)
    type = Column(Text)
    alignment = Column(Text)

    armor_class = Column(JSONB)  # array of objects [{type, value}]
    hit_points = Column(Integer)
    hit_dice = Column(Text)
    hit_points_roll = Column(Text)
    speed = Column(JSONB)  # object with walk, fly, swim, burrow, hover

    strength = Column(Integer)
    dexterity = Column(Integer)
    constitution = Column(Integer)
    intelligence = Column(Integer)
    wisdom = Column(Integer)
    charisma = Column(Integer)

    proficiencies = Column(JSONB)  # array of objects with value and proficiency
    damage_vulnerabilities = Column(JSONB)  # array of strings
    damage_resistances = Column(JSONB)  # array of strings
    damage_immunities = Column(JSONB)  # array of strings
    condition_immunities = Column(JSONB)  # array of objects with {index, name, url}

    senses = Column(JSONB)  # object with darkvision, blindsight, passive_perception
    languages = Column(Text)
    challenge_rating = Column(Integer)
    proficiency_bonus = Column(Integer)
    xp = Column(Integer)

    special_abilities = Column(JSONB)  # array of objects with name, desc, usage, damage
    actions = Column(
        JSONB
    )  # array of objects with attacks, multiattacks, breath weapons, etc.
    legendary_actions = Column(JSONB)  # array of objects with legendary actions
    reactions = Column(JSONB)  # array of objects with reactions
    forms = Column(JSONB)  # array (normally empty)

    image = Column(Text)
    url = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)


class AllMonsterscastroulloaaaron(Base):
    __tablename__ = "castroulloaaaron_allmonsters"
    id = Column(Integer, primary_key=True)
    json_data = Column(JSON, nullable=False)


class Monsterscastroulloaaaron(Base):
    __tablename__ = "castroulloaaaron_monsters"
    id = Column(String, primary_key=True)
    json_data = Column(JSON, nullable=False)


class RandallBrenesDnD(Base):
    __tablename__ = "randallbrenes_dnd_monsters"
    index = Column(String, primary_key=True)
    name = Column(String)
    url = Column(String)
    json_data = Column(JSON, nullable=True)


class Monster_majocr(Base):
    __tablename__ = "monster_majocr"
    index = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    data = Column(JSON, nullable=False)


class MonsterList_majocr(Base):
    __tablename__ = "monster_list_majocr"
    index = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)


class MonsterDanrodjim(Base):
    __tablename__ = "monsters_danrodjim"
    id = Column(Integer, primary_key=True)
    index = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    url = Column(String, unique=True, nullable=False)
    data = Column(JSONB)


class MonstersCrisarias(Base):
    __tablename__ = "monsters_crisarias"
    index = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    body = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class MonstersListCrisarias(Base):
    __tablename__ = "monsters_list_crisarias"
    index = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
