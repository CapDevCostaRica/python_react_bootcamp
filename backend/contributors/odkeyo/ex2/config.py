import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

_engine: Engine | None = None

def db_url_from_env() -> str:
    user = os.environ["POSTGRES_USER"]
    pwd  = os.environ["POSTGRES_PASSWORD"]
    host = os.environ["POSTGRES_HOST"]
    port = os.environ["POSTGRES_PORT"]
    db   = os.environ["POSTGRES_DB"]
    return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}"

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(db_url_from_env(), future=True)
    return _engine

def get_session():
    return Session(get_engine())