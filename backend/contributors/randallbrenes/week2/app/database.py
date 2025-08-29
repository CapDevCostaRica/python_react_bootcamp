import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

user = os.environ.get("POSTGRES_USER", "postgres")
password = os.environ.get("POSTGRES_PASSWORD", "postgres")
host = os.environ.get("POSTGRES_HOST", "localhost")
port = os.environ.get("POSTGRES_PORT", "5432")
db = os.environ.get("POSTGRES_DB", "postgres")

DATABASE_URL = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()
