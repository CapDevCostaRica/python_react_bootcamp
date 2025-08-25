# DB Engine
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

PG_HOST = os.getenv("POSTGRES_HOST", "flask_db")
PG_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
PG_DB   = os.getenv("POSTGRES_DB", "postgres")

DATABASE_URL = f"postgresql+psycopg://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
