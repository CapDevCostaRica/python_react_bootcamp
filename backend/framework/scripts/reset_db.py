
import os
import subprocess
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

user = os.environ.get("POSTGRES_USER", "postgres")
password = os.environ.get("POSTGRES_PASSWORD", "postgres")
host = os.environ.get("POSTGRES_HOST", "localhost")
port = os.environ.get("POSTGRES_PORT", "5432")
db = os.environ.get("POSTGRES_DB", "postgres")

DATABASE_URL = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"

def reset_database():
    engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as conn:
            conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS public;"))
        print("Database schema reset.")
    except ProgrammingError as pe:
        print(f"Error while resetting DB: {pe}")

def run_alembic_upgrade(path):
    print(f"Running alembic upgrade head in {path}")
    subprocess.run(["alembic", "upgrade", "head"], cwd=path, check=True)

if __name__ == "__main__":
    reset_database()
    framework_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    run_alembic_upgrade(framework_dir)

    seeds_path = os.path.join(framework_dir, "seeds.py")
    if os.path.exists(seeds_path):
        print(f"Running seeds.py in {framework_dir}")
        subprocess.run(["python", seeds_path], check=True)

    app_folder = os.environ.get("APPLICATION_FOLDER")
    if app_folder:
        app_folder_path = os.path.join(framework_dir, "..", "contributors", app_folder)
        alembic_ini_path = os.path.join(app_folder_path, "alembic.ini")
        if os.path.exists(alembic_ini_path):
            run_alembic_upgrade(app_folder_path)
        app_seeds_path = os.path.join(app_folder_path, "seeds.py")
        if os.path.exists(app_seeds_path):
            print(f"Running seeds.py in {app_folder_path}")
            subprocess.run(["python", app_seeds_path], check=True)
