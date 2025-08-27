from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MotivationalPhrase(Base):
    __tablename__ = 'dmuri_motivational_phrases'
    id = Column(Integer, primary_key=True)
    phrase = Column(String)


class DMuriMonstersList(Base):
    __tablename__ = 'dmrui_monsters_list'
    id = Column(Integer, primary_key=True)
    data = Column(JSON, nullable=False)
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class DMuriMonster(Base):
    __tablename__ = 'monsters'
    index = Column(String(100), primary_key=True)
    data = Column(JSON, nullable=False)
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
