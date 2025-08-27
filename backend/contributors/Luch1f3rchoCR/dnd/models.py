from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, JSON, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column
from framework.database import Base, engine


class MonsterCache(Base):
    __tablename__ = "monster_cache"
    __table_args__ = (UniqueConstraint("key", name="uq_monster_cache_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"), nullable=False
    )



Base.metadata.create_all(bind=engine)