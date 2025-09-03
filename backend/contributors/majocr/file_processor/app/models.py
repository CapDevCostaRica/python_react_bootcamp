from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class People_majocr(Base):
    __tablename__ = 'people_majocr'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    eye_color = Column(String, nullable=False)
    hair_color = Column(String, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    nationality = Column(String, nullable=False)

    studies = relationship("Study_majocr", back_populates="person") # One-to-many relationship with Study_majocr
    hobbies = relationship("Person_Hobby_Association_majocr", back_populates="person") # Many-to-many relationship with Hobby_majocr
    foods = relationship("Person_Food_Association_majocr", back_populates="person") # Many-to-many relationship with Food_majocr
    family = relationship("Family_majocr", back_populates="person") # One-to-many relationship with Family_majocr

class Study_majocr(Base):
    __tablename__ = 'study_majocr'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('people_majocr.id'), nullable=False)
    institution = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    
    person = relationship("People_majocr", back_populates="studies")

class Hobby_majocr(Base):
    __tablename__ = 'hobby_majocr'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    people = relationship("Person_Hobby_Association_majocr", back_populates="hobby")

class Person_Hobby_Association_majocr(Base):
    __tablename__ = 'person_hobby_association_majocr'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('people_majocr.id'), nullable=False)
    hobby_id = Column(Integer, ForeignKey('hobby_majocr.id'), nullable=False)
    person = relationship("People_majocr", back_populates="hobbies")
    hobby = relationship("Hobby_majocr", back_populates="people")

class Food_majocr(Base):
    __tablename__ = 'food_majocr'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    people = relationship("Person_Food_Association_majocr", back_populates="food")

class Person_Food_Association_majocr(Base):
    __tablename__ = 'person_food_association_majocr'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('people_majocr.id'), nullable=False)
    food_id = Column(Integer, ForeignKey('food_majocr.id'), nullable=False) 

    person = relationship("People_majocr", back_populates="foods")
    food = relationship("Food_majocr", back_populates="people")

class Family_majocr(Base):
    __tablename__ = 'family_majocr'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('people_majocr.id'), nullable=False)
    relation = Column(String, nullable=False)  # e.g., father, mother, sibling
    name = Column(String, nullable=False)

    person = relationship("People_majocr", back_populates="family")