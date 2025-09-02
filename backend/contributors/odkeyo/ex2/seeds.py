import sys, os
from pathlib import Path
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session
from app.models import (
    Base,
    odkeyo_ex2Person as Person,
    odkeyo_ex2Physical as Physical,
    odkeyo_ex2Study as Study,
    odkeyo_ex2Family as Family,
    odkeyo_ex2FavoriteFood as FavoriteFood,
    odkeyo_ex2Hobby as Hobby,
)

def _read_csv_dicts(path: Path):
    import csv
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield {k: (v if v != "" else None) for k, v in row.items()}

def _batch_insert_unique(session: Session, Model, rows_iter, keyfunc, normalize=None, batch_size=1000):
    seen = set(); batch = []
    for r in rows_iter:
        if normalize: r = normalize(r)
        k = keyfunc(r)
        if k in seen: continue
        seen.add(k); batch.append(r)
        if len(batch) >= batch_size:
            session.bulk_insert_mappings(Model, batch)
            session.commit(); batch.clear()
    if batch:
        session.bulk_insert_mappings(Model, batch)
        session.commit()

def reset_db_and_seed():
    user = os.environ.get("POSTGRES_USER", "postgres")
    pwd  = os.environ.get("POSTGRES_PASSWORD", "postgres")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db   = os.environ.get("POSTGRES_DB", "postgres")
    db_url = f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}"

    engine = create_engine(db_url, future=True)
    Base.metadata.create_all(engine)

    files_dir = Path(__file__).resolve().parent / "files"

    with Session(engine) as session:
        for Model in (Hobby, FavoriteFood, Family, Study, Physical, Person):
            session.execute(delete(Model))
        session.commit()

        people_rows = list(_read_csv_dicts(files_dir / "people_data.csv"))
        session.bulk_insert_mappings(Person, people_rows)
        session.commit()

        phys_by_pid = {}
        for r in _read_csv_dicts(files_dir / "physical_data.csv"):
            r["person_id"] = int(r["person_id"])
            r["age"] = int(r["age"]) if r["age"] else None
            r["height_cm"] = float(r["height_cm"]) if r["height_cm"] else None
            r["weight_kg"] = float(r["weight_kg"]) if r["weight_kg"] else None
            phys_by_pid[r["person_id"]] = r
        session.bulk_insert_mappings(Physical, list(phys_by_pid.values()))
        session.commit()

        _batch_insert_unique(
            session, Study, _read_csv_dicts(files_dir / "studies_data.csv"),
            keyfunc=lambda r: (int(r["person_id"]), r["degree"], r["institution"]),
            normalize=lambda r: {**r, "person_id": int(r["person_id"])}
        )

        _batch_insert_unique(
            session, Family, _read_csv_dicts(files_dir / "family_data.csv"),
            keyfunc=lambda r: (int(r["person_id"]), r["relation"], r["name"]),
            normalize=lambda r: {**r, "person_id": int(r["person_id"])}
        )

        _batch_insert_unique(
            session, FavoriteFood, _read_csv_dicts(files_dir / "favorite_data.csv"),
            keyfunc=lambda r: (int(r["person_id"]), r["food"]),
            normalize=lambda r: {**r, "person_id": int(r["person_id"])}
        )

        _batch_insert_unique(
            session, Hobby, _read_csv_dicts(files_dir / "hobbies_data.csv"),
            keyfunc=lambda r: (int(r["person_id"]), r["hobby"]),
            normalize=lambda r: {**r, "person_id": int(r["person_id"])}
        )

    print("DB reset + seed")


if __name__ == "__main__":
    reset_db_and_seed()