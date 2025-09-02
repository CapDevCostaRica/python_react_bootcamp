import os
from sqlalchemy import create_engine

def db_url_from_env() -> str:
    user = os.environ["POSTGRES_USER"]
    pwd  = os.environ["POSTGRES_PASSWORD"]
    host = os.environ["POSTGRES_HOST"]
    port = os.environ["POSTGRES_PORT"]
    db   = os.environ["POSTGRES_DB"]
    return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}"

def get_engine():
    return create_engine(db_url_from_env(), future=True)