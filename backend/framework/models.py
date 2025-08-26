from sqlalchemy import Column, Integer, String, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MotivationalPhrase(Base):
    __tablename__ = 'motivational_phrases'
    id = Column(Integer, primary_key=True)
    phrase = Column(String)

class WainerMora_Monsters(Base):
    __tablename__ = 'wainermora_monsters'
    id = Column(Integer, primary_key=True)
    index = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    size = Column(String)
    type = Column(String)
    subtype = Column(String)
    alignment = Column(String)
    armor_class = Column(JSON)  # Can be complex with dex_bonus, etc.
    hit_points = Column(Integer)
    hit_dice = Column(String)
    hit_points_roll = Column(String)
    speed = Column(JSON)  # Complex object with walk, fly, etc.
    strength = Column(Integer)
    dexterity = Column(Integer)
    constitution = Column(Integer)
    intelligence = Column(Integer)
    wisdom = Column(Integer)
    charisma = Column(Integer)
    proficiencies = Column(JSON)
    damage_vulnerabilities = Column(JSON)
    damage_resistances = Column(JSON)
    damage_immunities = Column(JSON)
    condition_immunities = Column(JSON)
    senses = Column(JSON)
    languages = Column(String)
    challenge_rating = Column(Float)
    proficiency_bonus = Column(Integer)
    xp = Column(Integer)
    special_abilities = Column(JSON)
    actions = Column(JSON)
    legendary_actions = Column(JSON)
    reactions = Column(JSON)
    forms = Column(JSON)
    spellcasting = Column(JSON)
    image = Column(String)
    url = Column(String)