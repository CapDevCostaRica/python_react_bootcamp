from sqlalchemy import Column, Integer, String, JSON, DateTime, func, JSON
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

class MonstersCrisarias(Base):
    __tablename__= 'monsters_crisarias'
    index = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    body = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())