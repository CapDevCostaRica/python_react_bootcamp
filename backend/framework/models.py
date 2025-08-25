from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

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