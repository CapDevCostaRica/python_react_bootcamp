from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, String, JSON, DateTime, func, JSON, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()
class MotivationalPhrase(Base):
    __tablename__ = 'motivational_phrases'
    id = Column(Integer, primary_key=True)
    phrase = Column(String)
