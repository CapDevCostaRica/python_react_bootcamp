from sqlalchemy import Column, Float, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MotivationalPhrase(Base):
    __tablename__ = 'motivational_phrases'
    id = Column(Integer, primary_key=True)
    phrase = Column(String)

class RandallBrenesDnD(Base):
    __tablename__ = 'randallbrenes_dnd_monsters'
    index = Column(String, primary_key=True)
    name = Column(String)
    desc = Column(String)
    size = Column(String)
    type = Column(String)
    subtype = Column(String)
    alignment = Column(String)
    armor_class = Column(JSONB)
    hit_points = Column(Integer)
    hit_dice = Column(String)
    hit_points_roll = Column(String)
    speed = Column(JSONB)
    strength = Column(Integer)
    dexterity = Column(Integer)
    constitution = Column(Integer)
    intelligence = Column(Integer)
    wisdom = Column(Integer)
    charisma = Column(Integer)
    proficiencies = Column(JSONB)
    damage_vulnerabilities = Column(JSONB)
    damage_resistances = Column(JSONB)
    damage_immunities = Column(JSONB)
    condition_immunities = Column(JSONB)
    senses = Column(JSONB)
    languages = Column(String)
    challenge_rating = Column(Float)
    proficiency_bonus = Column(Integer)
    xp = Column(Integer)
    special_abilities = Column(JSONB)
    actions = Column(JSONB)
    legendary_actions = Column(JSONB)
    image = Column(String)
    url = Column(String)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    forms = Column(JSONB)
    reactions = Column(JSONB)    