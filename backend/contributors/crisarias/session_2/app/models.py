from sqlalchemy import Column, ForeignKey, Index, Integer, Identity, Text, DateTime, func, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Person(Base):
    __tablename__= 'person'
    id = Column(Integer, primary_key=True)
    full_name = Column(Text, nullable=False)
    eye_color = Column(Text)
    hair_color = Column(Text)
    age = Column(Integer)
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    nationality = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
Index('ix_person_eye_color', Person.eye_color)
Index('ix_person_hair_color', Person.hair_color)
Index('ix_person_age', Person.age)
Index('ix_person_height_cm', Person.height_cm)
Index('ix_person_weight_kg', Person.weight_kg)
Index('ix_person_nationality', Person.nationality)


class Study(Base):
    __tablename__= 'study'
    id = Column(Integer,Identity(), primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    degree = Column(Text, nullable=False)
    institution = Column(Text, nullable=False)
Index('ix_study_degree', Study.degree)
Index('ix_study_institution', Study.institution)

class Family(Base):
    __tablename__= 'family'
    id = Column(Integer,Identity(), primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    relation = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
Index('ix_family_relation', Family.relation)

class FavoriteFood(Base):
    __tablename__= 'favorite_food'
    id = Column(Integer, Identity(), primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    food = Column(Text, nullable=False)
Index('ix_favorite_food_food', FavoriteFood.food)

class Hobby(Base):
    __tablename__= 'hobby'
    id = Column(Integer, Identity(), primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    hobby = Column(Text, nullable=False)
Index('ix_hobby_hobby', Hobby.hobby)