from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, String, JSON, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()
class MotivationalPhrase(Base):
    __tablename__ = 'motivational_phrases'
    id = Column(Integer, primary_key=True)
    phrase = Column(String)

class kevinWalshMunozMonsterList(Base):
    __tablename__ = 'kevinWalshMunozMonsters'

    index = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)

class kevinWalshMunozMonster(Base):
    __tablename__ = 'kevinWalshMunozMonster'

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
    actions = Column(JSONB)  # array of objects with attacks, multiattacks, breath weapons, etc.
    legendary_actions = Column(JSONB)  # array of objects with legendary actions
    reactions = Column(JSONB)  # array of objects with reactions
    forms = Column(JSONB)  # array (normally empty)
    
    image = Column(Text)
    url = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)

class AllMonsterscastroulloaaaron(Base):
    __tablename__ = 'castroulloaaaron_allmonsters'
    id = Column(Integer, primary_key=True)
    json_data = Column(JSON, nullable=False)


class Monsterscastroulloaaaron(Base):
    __tablename__ = 'castroulloaaaron_monsters'
    id = Column(String, primary_key=True)
    json_data = Column(JSON, nullable=False)

class RandallBrenesDnD(Base):
    __tablename__ = 'randallbrenes_dnd_monsters'
    index = Column(String, primary_key=True)
    name = Column(String)
    url = Column(String)
    json_data = Column(JSON, nullable=True)   

class Monster_majocr(Base):
    __tablename__ = 'monster_majocr'
    index = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    data = Column(JSON, nullable=False)

class MonsterList_majocr(Base):
    __tablename__ = 'monster_list_majocr'
    index = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)

class MonsterDanrodjim(Base):
    __tablename__ = 'monsters_danrodjim'
    id = Column(Integer, primary_key=True)
    index = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    url = Column(String, unique=True, nullable=False)
    data = Column(JSONB)

    
class AllMonstersdanielmadriz(Base):
    __tablename__ = 'danielmadriz_allmonsters'
    id = Column(String, primary_key=True)
    json_data = Column(JSON, nullable=False)

class Monstersdanielmadriz(Base):
    __tablename__ = 'danielmadriz_monsters'
    index = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)    
    data = Column(JSON, nullable=False)
