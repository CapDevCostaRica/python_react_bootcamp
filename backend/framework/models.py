from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class MotivationalPhrase(Base):
    __tablename__ = 'motivational_phrases'
    id = Column(Integer, primary_key=True)
    phrase = Column(String)

class MonsterDanrodjim(Base):
    __tablename__ = 'monsters_danrodjim'
    id = Column(Integer, primary_key=True)
    index = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    url = Column(String, unique=True, nullable=False)
    data = Column(JSONB)