from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from .db import Base

class MonsterCache(Base):
    __tablename__ = "luch1f3rchocr_monster_cache"
    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False)
    payload = Column(JSONB, nullable=False)
    cached_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("key", name="uq_luch1f3rchocr_monster_key"),)
