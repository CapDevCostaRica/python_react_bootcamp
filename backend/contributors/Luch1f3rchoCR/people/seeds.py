#!/usr/bin/env python3

import csv, re, sys
from pathlib import Path
from typing import Iterator, Dict, Any, Tuple, Set
from sqlalchemy import select, text
from sqlalchemy.orm import Session

try:
    from .app.database import SessionLocal
    from .app.models import People, Favorite, Hobbies, Family, Studies
except ImportError:
    ROOT = Path(__file__).resolve().parent
    sys.path.append(str(ROOT))
    from app.database import SessionLocal
    from app.models import People, Favorite, Hobbies, Family, Studies

DATA_DIR = Path(__file__).parent / "data"

def _normrow(row: dict) -> dict:
    return {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}

def int_or_none(v):
    if v is None:
        return None
    m = re.search(r"-?\d+", str(v).strip())
    return int(m.group()) if m else None

def _gentilic(nat_raw: str | None) -> str | None:
    if not nat_raw:
        return None
    s = nat_raw.strip().lower()
    table = {
        "méxico":"Mexican","mexico":"Mexican","mexican":"Mexican",
        "spain":"Spanish","españa":"Spanish","spanish":"Spanish",
        "usa":"American","us":"American","united states":"American",
        "united states of america":"American","america":"American","american":"American",
        "brazil":"Brazilian","brasil":"Brazilian","brazilian":"Brazilian",
        "germany":"German","german":"German",
        "france":"French","french":"French",
        "canada":"Canadian","canadian":"Canadian",
        "nigeria":"Nigerian","nigerian":"Nigerian",
    }
    return table.get(s) or s.title()

def _csv(path: Path) -> Iterator[Dict[str, Any]]:
    if not path.exists():
        return iter(())
    with path.open(newline="", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            yield _normrow(raw)

def _titlecase(s: str) -> str:
    parts = (s or "").split()
    return " ".join(p.capitalize() for p in parts)

def _ensure_unique_indexes(s: Session):
    specs = [
        (Family.__tablename__,   "ux_family_unique",   ["person_id","relation","name"]),
        (Favorite.__tablename__, "ux_favorite_unique", ["person_id","food"]),
        (Hobbies.__tablename__,  "ux_hobbies_unique",  ["person_id","hobby"]),
        (Studies.__tablename__,  "ux_studies_unique",  ["person_id","degree","institution"]),
    ]
    dialect = s.bind.dialect.name if s.bind is not None else ""
    for tbl, idx, cols in specs:
        try:
            if dialect == "postgresql":
                sql = f"""
                DO $$
                BEGIN
                  IF to_regclass('public.{tbl}') IS NOT NULL THEN
                    EXECUTE 'CREATE UNIQUE INDEX IF NOT EXISTS {idx} ON {tbl} ({", ".join(cols)})';
                  END IF;
                END $$;
                """
                s.execute(text(sql))
            else:
                sql = f"CREATE UNIQUE INDEX IF NOT EXISTS {idx} ON {tbl} ({', '.join(cols)})"
                s.execute(text(sql))
            s.flush()
        except Exception:
            s.rollback()
    try:
        s.execute(text("SELECT 1"))
    except Exception:
        s.rollback()

def load_people(s: Session):
    seen: Set[int] = set()
    for row in _csv(DATA_DIR / "people_data.csv"):
        if not row.get("id"):
            continue
        pid = int(row["id"])
        if pid in seen:
            continue
        seen.add(pid)
        p = s.get(People, pid)
        if not p:
            p = People(id=pid, full_name=row.get("full_name") or None)
            s.add(p)
        else:
            if row.get("full_name"):
                p.full_name = row["full_name"]

def load_physical(s: Session):
    for row in _csv(DATA_DIR / "physical_data.csv"):
        pid = int_or_none(row.get("person_id") or row.get("id"))
        if pid is None:
            continue
        p = s.get(People, pid)
        if not p:
            p = People(id=pid)
            s.add(p)
        if row.get("eye_color"):
            p.eye_color = row["eye_color"]
        if row.get("hair_color"):
            p.hair_color = row["hair_color"]
        age = int_or_none(row.get("age"))
        if age is not None:
            p.age = age
        h = int_or_none(row.get("height_cm") or row.get("height"))
        if h is not None:
            p.height_cm = h
        w = int_or_none(row.get("weight_kg") or row.get("weight"))
        if w is not None:
            p.weight_kg = w
        nat = _gentilic(row.get("nationality"))
        if nat:
            p.nationality = nat

def load_favorites(s: Session):
    seen: Set[Tuple[int,str]] = set()
    for row in _csv(DATA_DIR / "favorite_data.csv"):
        if not row.get("person_id"):
            continue
        pid = int(row["person_id"])
        food = (row.get("food") or "").strip()
        if not food:
            continue
        key = (pid, food)
        if key in seen:
            continue
        seen.add(key)
        exists = s.execute(
            select(Favorite.id).where(Favorite.person_id == pid, Favorite.food == food)
        ).first()
        if not exists:
            s.add(Favorite(person_id=pid, food=food))

def load_hobbies(s: Session):
    seen: Set[Tuple[int,str]] = set()
    for row in _csv(DATA_DIR / "hobbies_data.csv"):
        if not row.get("person_id"):
            continue
        pid = int(row["person_id"])
        hobby = (row.get("hobby") or "").strip()
        if not hobby:
            continue
        key = (pid, hobby)
        if key in seen:
            continue
        seen.add(key)
        exists = s.execute(
            select(Hobbies.id).where(Hobbies.person_id == pid, Hobbies.hobby == hobby)
        ).first()
        if not exists:
            s.add(Hobbies(person_id=pid, hobby=hobby))

def load_family(s: Session):
    seen: Set[Tuple[int,str,str]] = set()
    for row in _csv(DATA_DIR / "family_data.csv"):
        if not row.get("person_id"):
            continue
        pid = int(row["person_id"])
        relation = (row.get("relation") or "").casefold()
        name = _titlecase(row.get("name") or "")
        if not relation or not name:
            continue
        key = (pid, relation, name)
        if key in seen:
            continue
        seen.add(key)
        exists = s.execute(
            select(Family.id).where(
                Family.person_id == pid, Family.relation == relation, Family.name == name
            )
        ).first()
        if not exists:
            s.add(Family(person_id=pid, relation=relation, name=name))

def load_studies(s: Session):
    seen: Set[Tuple[int,str,str]] = set()
    for row in _csv(DATA_DIR / "studies_data.csv"):
        if not row.get("person_id"):
            continue
        pid = int(row["person_id"])
        degree = (row.get("degree") or "").strip()
        inst = (row.get("institution") or "").strip()
        if not degree and not inst:
            continue
        key = (pid, degree, inst)
        if key in seen:
            continue
        seen.add(key)
        exists = s.execute(
            select(Studies.id).where(
                Studies.person_id == pid,
                Studies.degree == degree,
                Studies.institution == inst,
            )
        ).first()
        if not exists:
            s.add(Studies(person_id=pid, degree=degree, institution=inst))

def run():
    with SessionLocal() as s:
        _ensure_unique_indexes(s)
        load_people(s); s.flush()
        load_physical(s); s.flush()
        load_favorites(s)
        load_hobbies(s)
        load_family(s)
        load_studies(s)
        s.commit()
        total, with_age, with_nat, with_eye, with_hair = s.execute(text("""
            SELECT
              count(*),
              count(age),
              count(NULLIF(TRIM(COALESCE(nationality,'')), '')),
              count(eye_color),
              count(hair_color)
            FROM people
        """)).one()
        print(f"[seeds] people={total} | age={with_age} | nat={with_nat} | eye={with_eye} | hair={with_hair}")

if __name__ == "__main__":
    run()
    print("Seeds completed.")