from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship

Base = declarative_base()

class Person(Base):
    __tablename__ = 'people'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    
    physical_attributes = relationship("PhysicalAttribute", uselist=False, back_populates="person")
    family_relations = relationship("FamilyRelation", back_populates="person")
    favorite_foods = relationship("FavoriteFood", back_populates="person")
    hobbies = relationship("Hobby", back_populates="person")
    education = relationship("Education", back_populates="person")

class PhysicalAttribute(Base):
    __tablename__ = 'physical_attributes'
    
    person_id = Column(Integer, ForeignKey('people.id'), primary_key=True)
    eye_color = Column(String(20), nullable=False)
    hair_color = Column(String(20), nullable=False)
    age = Column(Integer, nullable=False)
    height_cm = Column(Integer, nullable=False)
    weight_kg = Column(Integer, nullable=False)
    nationality = Column(String(50), nullable=False)
    
    person = relationship("Person", back_populates="physical_attributes")

class FamilyRelation(Base):
    __tablename__ = 'family_relations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('people.id'), nullable=False)
    relation_type = Column(String(20), nullable=False)
    relative_name = Column(String(255), nullable=False)
    
    person = relationship("Person", back_populates="family_relations")

class FavoriteFood(Base):
    __tablename__ = 'favorite_foods'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('people.id'), nullable=False)
    food = Column(String(50), nullable=False)
    
    person = relationship("Person", back_populates="favorite_foods")

class Hobby(Base):
    __tablename__ = 'hobbies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('people.id'), nullable=False)
    hobby = Column(String(50), nullable=False)
    
    person = relationship("Person", back_populates="hobbies")

class Education(Base):
    __tablename__ = 'education'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('people.id'), nullable=False)
    degree = Column(String(100), nullable=False)
    institution = Column(String(255), nullable=False)
    
    person = relationship("Person", back_populates="education")