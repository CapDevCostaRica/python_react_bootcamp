from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Person(Base):
    __tablename__ = "persons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    eye_color: Mapped[str] = mapped_column(String, nullable=False)
    hair_color: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    height_cm: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[int] = mapped_column(Integer, nullable=False)
    nationality: Mapped[str] = mapped_column(String, nullable=False)
    foods: Mapped[list["Food"]] = relationship(back_populates="person")
    hobbies: Mapped[list["Hobby"]] = relationship(back_populates="person")
    family: Mapped[list["Family"]] = relationship(back_populates="person")
    studies: Mapped[list["Study"]] = relationship(back_populates="person")

class Food(Base):
    __tablename__ = "foods"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("persons.id"))
    person: Mapped["Person"] = relationship(back_populates="foods")

class Hobby(Base):
    __tablename__ = "hobbies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("persons.id"))
    person: Mapped["Person"] = relationship(back_populates="hobbies")

class Family(Base):
    __tablename__ = "family"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    relation: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("persons.id"))
    person: Mapped["Person"] = relationship(back_populates="family")

class Study(Base):
    __tablename__ = "studies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    degree: Mapped[str] = mapped_column(String, nullable=False)
    institution: Mapped[str] = mapped_column(String, nullable=False)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("persons.id"))
    person: Mapped["Person"] = relationship(back_populates="studies")