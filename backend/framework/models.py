from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MotivationalPhrase(Base):
    __tablename__ = 'motivational_phrases'
    id = Column(Integer, primary_key=True)
    phrase = Column(String)


# Monster cache for randymorales proxy
class randymorales_MonsterCache(Base):
    __tablename__ = 'randymorales_monster_cache'
    id = Column(Integer, primary_key=True)
    monster_index = Column(String, unique=True, nullable=False)
    monster_data = Column(String, nullable=False)  # Store JSON as string

class randymorales_MonsterListCache(Base):
    __tablename__ = 'randymorales_monster_list_cache'
    id = Column(Integer, primary_key=True)
    resource = Column(String, unique=True, nullable=False)
    list_data = Column(String, nullable=False)  # Store JSON as string
