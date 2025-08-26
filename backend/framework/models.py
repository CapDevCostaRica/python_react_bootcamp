from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MotivationalPhrase(Base):
    __tablename__ = 'motivational_phrases'
    id = Column(Integer, primary_key=True)
    phrase = Column(String)

class AndresnbozaMonster(Base):
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'index': self.index,
            'name': self.name,
            'size': self.size,
            'type': self.type,
            'alignment': self.alignment,
            'armor_class': json.loads(self.armor_class) if self.armor_class else None,
            'hit_points': self.hit_points,
            'hit_dice': self.hit_dice,
            'hit_points_roll': self.hit_points_roll,
            'speed': json.loads(self.speed) if self.speed else None,
            'strength': self.strength,
            'dexterity': self.dexterity,
            'constitution': self.constitution,
            'intelligence': self.intelligence,
            'wisdom': self.wisdom,
            'charisma': self.charisma,
            'proficiencies': json.loads(self.proficiencies) if self.proficiencies else None,
            'damage_vulnerabilities': json.loads(self.damage_vulnerabilities) if self.damage_vulnerabilities else None,
            'damage_resistances': json.loads(self.damage_resistances) if self.damage_resistances else None,
            'damage_immunities': json.loads(self.damage_immunities) if self.damage_immunities else None,
            'condition_immunities': json.loads(self.condition_immunities) if self.condition_immunities else None,
            'senses': json.loads(self.senses) if self.senses else None,
            'languages': self.languages,
            'challenge_rating': self.challenge_rating,
            'proficiency_bonus': self.proficiency_bonus,
            'xp': self.xp,
            'special_abilities': json.loads(self.special_abilities) if self.special_abilities else None,
            'actions': json.loads(self.actions) if self.actions else None,
            'legendary_actions': json.loads(self.legendary_actions) if self.legendary_actions else None,
            'image': self.image,
            'url': self.url,
            'updated_at': self.updated_at,
            'forms': json.loads(self.forms) if self.forms else None,
            'reactions': json.loads(self.reactions) if self.reactions else None
        }
    __tablename__ = 'andresnboza_monster'
    id = Column(Integer, primary_key=True)
    index = Column(String)
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

    @staticmethod
    def from_api_data(data, normalize_name_func=None):
        import json
        return AndresnbozaMonster(
            index=data.get('index'),
            name=normalize_name_func(data.get('name')) if normalize_name_func else data.get('name'),
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