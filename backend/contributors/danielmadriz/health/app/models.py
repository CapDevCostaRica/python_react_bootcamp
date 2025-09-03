from sqlalchemy import Column, Integer, String, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship,declarative_base

Base = declarative_base()


class Person(Base):
    __tablename__ = 'danielmadriz_person'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    
    # Relationships
    physical_profile = relationship("PhysicalProfile", back_populates="person", uselist=False)
    favorite_foods = relationship("FavoriteFood", back_populates="person")
    hobbies = relationship("Hobby", back_populates="person")
    family_relations = relationship("FamilyRelation", back_populates="person")
    studies = relationship("Study", back_populates="person")
    
    # Indexes
    __table_args__ = (
        Index('idx_person_full_name', 'full_name'),
    )


class PhysicalProfile(Base):
    __tablename__ = 'danielmadriz_physical_profile'
    
    person_id = Column(Integer, ForeignKey('danielmadriz_person.id'), primary_key=True)
    eye_color = Column(String(50))
    hair_color = Column(String(50))
    age = Column(Integer)
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    nationality = Column(String(100))
    
    # Relationships
    person = relationship("Person", back_populates="physical_profile")
    
    # Indexes
    # TODO Re-Evaluate if all this indexes are needed once we implement the endpoints
    __table_args__ = (
        Index('idx_physical_profile_eye_color', 'eye_color'),
        Index('idx_physical_profile_hair_color', 'hair_color'),
        Index('idx_physical_profile_age', 'age'),
        Index('idx_physical_profile_nationality', 'nationality'),
    )


class FavoriteFood(Base):
    __tablename__ = 'danielmadriz_favorite_food'
    
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('danielmadriz_person.id'), nullable=False)
    food = Column(String(255), nullable=False)
    
    # Relationships
    person = relationship("Person", back_populates="favorite_foods")
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('person_id', 'food', name='uq_person_food'),
        Index('idx_favorite_food_food', 'food'),
    )


class Hobby(Base):
    __tablename__ = 'danielmadriz_hobby'
    
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('danielmadriz_person.id'), nullable=False)
    hobby = Column(String(255), nullable=False)
    
    # Relationships
    person = relationship("Person", back_populates="hobbies")
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('person_id', 'hobby', name='uq_person_hobby'),
        Index('idx_hobby_hobby', 'hobby'),
    )


class FamilyRelation(Base):
    __tablename__ = 'danielmadriz_family_relation'
    
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('danielmadriz_person.id'), nullable=False)
    relation = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    
    # Relationships
    person = relationship("Person", back_populates="family_relations")
    
    # Indexes
    __table_args__ = (
        Index('idx_family_relation_person_relation', 'person_id', 'relation'),
    )


class Study(Base):
    __tablename__ = 'danielmadriz_study'
    
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('danielmadriz_person.id'), nullable=False)
    degree = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    
    # Relationships
    person = relationship("Person", back_populates="studies")
    
    # Constraints and Indexes
     # TODO Re-Evaluate if all this indexes are needed once we implement the endpoints
    __table_args__ = (
        UniqueConstraint('person_id', 'degree', 'institution', name='uq_person_degree_institution'),
        Index('idx_study_degree', 'degree'),
        Index('idx_study_institution', 'institution'),
    )