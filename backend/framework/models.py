from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, String, JSON, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
import json
from datetime import datetime

Base = declarative_base()
class MotivationalPhrase(Base):
    __tablename__ = 'motivational_phrases'
    id = Column(Integer, primary_key=True)
    phrase = Column(String)

class AndresnbozaMonster(Base):
    __tablename__ = 'andresnboza_monster'
    index = Column(String, primary_key=True)
    name = Column(String)
    size = Column(String)
    type = Column(String)
    alignment = Column(String)
    armor_class = Column(String)
    hit_points = Column(Integer)
    hit_dice = Column(String)
    hit_points_roll = Column(String)
    speed = Column(String)
    strength = Column(Integer)
    dexterity = Column(Integer)
    constitution = Column(Integer)
    intelligence = Column(Integer)
    wisdom = Column(Integer)
    charisma = Column(Integer)
    proficiencies = Column(String)
    damage_vulnerabilities = Column(String)
    damage_resistances = Column(String)
    damage_immunities = Column(String)
    condition_immunities = Column(String)
    senses = Column(String)
    languages = Column(String)
    challenge_rating = Column(Integer)
    proficiency_bonus = Column(Integer)
    xp = Column(Integer)
    special_abilities = Column(String)
    actions = Column(String)
    legendary_actions = Column(String)
    image = Column(String)
    url = Column(String)
    updated_at = Column(String)
    forms = Column(String)
    reactions = Column(String)

    def to_dict(self):
        return {
            'index': self.index,
            'name': self.name,
            'size': self.size,
            'type': self.type,
            'alignment': self.alignment,
            'armor_class': self.armor_class,
            'hit_points': self.hit_points,
            'hit_dice': self.hit_dice,
            'hit_points_roll': self.hit_points_roll,
            'speed': self.speed,
            'strength': self.strength,
            'dexterity': self.dexterity,
            'constitution': self.constitution,
            'intelligence': self.intelligence,
            'wisdom': self.wisdom,
            'charisma': self.charisma,
            'proficiencies': self.proficiencies,
            'damage_vulnerabilities': self.damage_vulnerabilities,
            'damage_resistances': self.damage_resistances,
            'damage_immunities': self.damage_immunities,
            'condition_immunities': self.condition_immunities,
            'senses': self.senses,
            'languages': self.languages,
            'challenge_rating': self.challenge_rating,
            'proficiency_bonus': self.proficiency_bonus,
            'xp': self.xp,
            'special_abilities': self.special_abilities,
            'actions': self.actions,
            'legendary_actions': self.legendary_actions,
            'image': self.image,
            'url': self.url,
            'updated_at': self.updated_at,
            'forms': self.forms,
            'reactions': self.reactions
        }

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
    proficiencies = Column(String) 
    damage_vulnerabilities = Column(String)
    damage_resistances = Column(String) 
    damage_immunities = Column(String)  
    condition_immunities = Column(String)
    senses = Column(String)  
    languages = Column(String)
    challenge_rating = Column(Integer)
    proficiency_bonus = Column(Integer)
    xp = Column(Integer)
    special_abilities = Column(String) 
    actions = Column(String)  
    legendary_actions = Column(String) 
    image = Column(String)
    url = Column(String)
    updated_at = Column(String)
    forms = Column(String)  
    reactions = Column(String) 

    @staticmethod
    def from_api_data(data):
        return AndresnbozaMonster(
            index=data.get('index'),
            name=data.get('name'),
            size=data.get('size'),
            type=data.get('type'),
            alignment=data.get('alignment'),
            armor_class=json.dumps(data.get('armor_class')),
            hit_points=data.get('hit_points'),
            hit_dice=data.get('hit_dice'),
            hit_points_roll=data.get('hit_points_roll'),
            speed=json.dumps(data.get('speed')),
            strength=data.get('strength'),
            dexterity=data.get('dexterity'),
            constitution=data.get('constitution'),
            intelligence=data.get('intelligence'),
            wisdom=data.get('wisdom'),
            charisma=data.get('charisma'),
            proficiencies=json.dumps(data.get('proficiencies')),
            damage_vulnerabilities=json.dumps(data.get('damage_vulnerabilities')),
            damage_resistances=json.dumps(data.get('damage_resistances')),
            damage_immunities=json.dumps(data.get('damage_immunities')),
            condition_immunities=json.dumps(data.get('condition_immunities')),
            senses=json.dumps(data.get('senses')),
            languages=data.get('languages'),
            challenge_rating=data.get('challenge_rating'),
            proficiency_bonus=data.get('proficiency_bonus'),
            xp=data.get('xp'),
            special_abilities=json.dumps(data.get('special_abilities')),
            actions=json.dumps(data.get('actions')),
            legendary_actions=json.dumps(data.get('legendary_actions')),
            image=data.get('image'),
            url=data.get('url'),
            updated_at=data.get('updated_at'),
            forms=json.dumps(data.get('forms')),
            reactions=json.dumps(data.get('reactions'))
        )
    
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
