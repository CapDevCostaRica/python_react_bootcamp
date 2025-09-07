import os, sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from .models import Base
except ImportError:
    here = os.path.dirname(__file__)
    if here not in sys.path:
        sys.path.insert(0, here)
    from models import Base


def _pg_url():
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    pwd  = os.getenv("POSTGRES_PASSWORD", "postgres")
    db   = os.getenv("POSTGRES_DB", "postgres")
    return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}"

DB_URL = os.getenv("DATABASE_URL", _pg_url())

if os.getenv("TEST_DATABASE_URL"):
    DB_URL = os.getenv("TEST_DATABASE_URL")
elif os.getenv("TESTING") == "1":
    DB_URL = "sqlite:///:memory:"

connect_args = {}
if DB_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DB_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def init_db():
    Base.metadata.create_all(bind=engine)