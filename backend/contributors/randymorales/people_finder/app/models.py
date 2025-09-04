from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class RandymoralesPerson(Base):
    __tablename__ = 'randymorales_people'

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)

    # Relationships
    physical_data = relationship("RandymoralesPhysicalData", back_populates="person", uselist=False)
    family_relations = relationship("RandymoralesFamilyRelation", back_populates="person")
    favorite_foods = relationship("RandymoralesFavoriteFood", back_populates="person")
    hobbies = relationship("RandymoralesHobby", back_populates="person")
    studies = relationship("RandymoralesStudy", back_populates="person")


class RandymoralesPhysicalData(Base):
    __tablename__ = 'randymorales_physical_data'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('randymorales_people.id'), nullable=False)
    eye_color = Column(String, nullable=False)
    hair_color = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    height_cm = Column(Integer, nullable=False)
    weight_kg = Column(Integer, nullable=False)
    nationality = Column(String, nullable=False)

    # Relationships
    person = relationship("RandymoralesPerson", back_populates="physical_data")


class RandymoralesFamilyRelation(Base):
    __tablename__ = 'randymorales_family_relations'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('randymorales_people.id'), nullable=False)
    relation = Column(String, nullable=False)  # mother, father, sister, etc.
    name = Column(String, nullable=False)

    # Relationships
    person = relationship("RandymoralesPerson", back_populates="family_relations")


class RandymoralesFavoriteFood(Base):
    __tablename__ = 'randymorales_favorite_foods'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('randymorales_people.id'), nullable=False)
    food = Column(String, nullable=False)

    # Relationships
    person = relationship("RandymoralesPerson", back_populates="favorite_foods")


class RandymoralesHobby(Base):
    __tablename__ = 'randymorales_hobbies'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('randymorales_people.id'), nullable=False)
    hobby = Column(String, nullable=False)

    # Relationships
    person = relationship("RandymoralesPerson", back_populates="hobbies")


class RandymoralesStudy(Base):
    __tablename__ = 'randymorales_studies'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('randymorales_people.id'), nullable=False)
    degree = Column(String, nullable=False)
    institution = Column(String, nullable=False)

    # Relationships
    person = relationship("RandymoralesPerson", back_populates="studies")