from xmlrpc.client import DateTime
from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MotivationalPhrase(Base):
    __tablename__ = 'motivational_phrases'
    id = Column(Integer, primary_key=True)
    phrase = Column(String)

class MonstersCrisarias(Base):
    __tablename__= 'monsters_crisarias'
    id = Column(String, primary_key=True)
    body = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())