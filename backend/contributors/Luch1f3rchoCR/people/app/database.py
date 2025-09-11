import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

user = os.environ.get("POSTGRES_USER", "postgres")
password = os.environ.get("POSTGRES_PASSWORD", "postgres")
host = os.environ.get("POSTGRES_HOST", "localhost")
port = os.environ.get("POSTGRES_PORT", "5432")
db = os.environ.get("POSTGRES_DB", "postgres")

url = os.environ.get(
    "SQLALCHEMY_DATABASE_URL",
    f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}",
)

engine = create_engine(url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base.metadata.bind = engine