from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MotivationalPhrase(Base):
    __tablename__ = 'motivational_phrases'
    id = Column(Integer, primary_key=True)
    phrase = Column(String)


class AllMonsterscastroulloaaaron(Base):
    __tablename__ = 'castroulloaaaron_allmonsters'
    id = Column(Integer, primary_key=True)
    json_data = Column(JSON, nullable=False)


class Monsterscastroulloaaaron(Base):
    __tablename__ = 'castroulloaaaron_monsters'
    id = Column(String, primary_key=True)
    json_data = Column(JSON, nullable=False)

class DMuriMonstersList(Base):
    __tablename__ = 'dmuri_monsters_list'
    id = Column(Integer, primary_key=True)
    data = Column(JSON, nullable=False)
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class DMuriMonster(Base):
    __tablename__ = 'dmuri_monsters'
    index = Column(String(100), primary_key=True)
    data = Column(JSON, nullable=False)
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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
