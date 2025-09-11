from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class odkeyo_ex2Person(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)

    physical = relationship("odkeyo_ex2Physical", back_populates="person", uselist=False, cascade="all, delete-orphan")
    studies = relationship("odkeyo_ex2Study", back_populates="person", cascade="all, delete-orphan")
    families = relationship("odkeyo_ex2Family", back_populates="person", cascade="all, delete-orphan")
    favorites = relationship("odkeyo_ex2FavoriteFood", back_populates="person", cascade="all, delete-orphan")
    hobbies = relationship("odkeyo_ex2Hobby", back_populates="person", cascade="all, delete-orphan")

class odkeyo_ex2Physical(Base):
    __tablename__ = "physical"
    person_id = Column(Integer, ForeignKey("people.id"), primary_key=True)
    eye_color = Column(String)
    hair_color = Column(String)
    age = Column(Integer)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    nationality = Column(String)

    person = relationship("odkeyo_ex2Person", back_populates="physical")

class odkeyo_ex2Study(Base):
    __tablename__ = "studies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey("people.id"), index=True)
    degree = Column(String)
    institution = Column(String)

    person = relationship("odkeyo_ex2Person", back_populates="studies")
    __table_args__ = (UniqueConstraint("person_id", "degree", "institution", name="uq_study"),)

class odkeyo_ex2Family(Base):
    __tablename__ = "families"
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey("people.id"), index=True)
    relation = Column(String)
    name = Column(String)

    person = relationship("odkeyo_ex2Person", back_populates="families")
    __table_args__ = (UniqueConstraint("person_id", "relation", "name", name="uq_family"),)

class odkeyo_ex2FavoriteFood(Base):
    __tablename__ = "favorite_foods"
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey("people.id"), index=True)
    food = Column(String, index=True)

    person = relationship("odkeyo_ex2Person", back_populates="favorites")
    __table_args__ = (UniqueConstraint("person_id", "food", name="uq_favorite_food"),)

class odkeyo_ex2Hobby(Base):
    __tablename__ = "hobbies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey("people.id"), index=True)
    hobby = Column(String, index=True)

    person = relationship("odkeyo_ex2Person", back_populates="hobbies")
    __table_args__ = (UniqueConstraint("person_id", "hobby", name="uq_hobby"),)