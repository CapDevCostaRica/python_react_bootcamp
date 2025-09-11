
from sqlalchemy import (
    Column, Integer, String, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class People(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    eye_color = Column(String, index=True)
    hair_color = Column(String, index=True)
    age = Column(Integer, index=True)
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    nationality = Column(String, index=True)

    favorites = relationship(
        "Favorite", back_populates="person",
        cascade="all, delete-orphan", passive_deletes=True
    )
    hobbies = relationship(
        "Hobbies", back_populates="person",
        cascade="all, delete-orphan", passive_deletes=True
    )
    families = relationship(
        "Family", back_populates="person",
        cascade="all, delete-orphan", passive_deletes=True
    )
    studies = relationship(
        "Studies", back_populates="person",
        cascade="all, delete-orphan", passive_deletes=True
    )

class Favorite(Base):
    __tablename__ = "favorite"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True)
    food = Column(String, nullable=False, index=True)

    person = relationship("People", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint("person_id", "food", name="uq_person_food"),
    )

class Hobbies(Base):
    __tablename__ = "hobbies"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True)
    hobby = Column(String, nullable=False, index=True)

    person = relationship("People", back_populates="hobbies")

    __table_args__ = (
        UniqueConstraint("person_id", "hobby", name="uq_person_hobby"),
    )

class Family(Base):
    __tablename__ = "family"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True)
    relation = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)

    person = relationship("People", back_populates="families")

class Studies(Base):
    __tablename__ = "studies"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True)
    degree = Column(String, index=True)
    institution = Column(String, index=True)

    person = relationship("People", back_populates="studies")


Index("ix_people_color_age_nat", People.eye_color, People.hair_color, People.age, People.nationality)