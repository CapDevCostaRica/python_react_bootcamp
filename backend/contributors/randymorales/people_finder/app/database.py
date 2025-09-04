import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database configuration - use environment variables like the framework
def get_database_url():
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ.get("POSTGRES_DB", "postgres")

    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"

# Create engine and session factory
engine = create_engine(get_database_url())
SessionLocal = sessionmaker(bind=engine)

def get_session():
    """Get a database session"""
    return SessionLocal()
