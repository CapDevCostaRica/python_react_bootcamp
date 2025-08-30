from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class People(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    eye_color = Column(String)
    hair_color = Column(String)
    age = Column(Integer)
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    nationality = Column(String)
    families = relationship("Family", back_populates="person")
    favorites = relationship("Favorite", back_populates="person")
    hobbies = relationship("Hobbies", back_populates="person")
    studies = relationship("Studies", back_populates="person")

class Family(Base):
    __tablename__ = 'family'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('people.id'))
    person = relationship("People", back_populates="families")
    relation = Column(String)
    name = Column(String)

class Favorite(Base):
    __tablename__ = 'favorite'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('people.id'))
    person = relationship("People", back_populates="favorites")
    food = Column(String)

class Hobbies(Base):
    __tablename__ = 'hobbies'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('people.id'))
    person = relationship("People", back_populates="hobbies")
    hobby = Column(String)

class Studies(Base):
    __tablename__ = 'studies'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('people.id'))
    person = relationship("People", back_populates="studies")
    degree = Column(String)
    institution = Column(String)
