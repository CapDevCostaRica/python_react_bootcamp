from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import os, sys
import requests
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

# DB Engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../framework")))
from database import Base, engine, SessionLocal
from models import MonsterCache


from contributors.Luch1f3rchoCR.dnd.validations import (
    HandlerRequestSchema,
    MonstersListSchema,
    MonsterDetailSchema,
)

CACHE_TTL = timedelta(hours=6)
UPSTREAM = "https://www.dnd5eapi.co/api"

app = Flask(__name__)
Base.metadata.create_all(bind=engine)

req_schema = HandlerRequestSchema()


@app.get("/")
def root():
    return jsonify({"ok": True, "msg": "Hello there, from Luch1f3rchoCR/dnd!"})


@app.post("/handler")
def handler():
    """
    OK:
      - {"resource": "monsters"}      -> get list
      - {"monster_index": "<string>"} -> get detail
    """
    raw = request.get_json(force=True, silent=True) or {}
    try:
        data = req_schema.load(raw)
    except ValidationError as err:
        return jsonify({"error": "invalid payload", "details": err.messages}), 400

    if data.get("resource") == "monsters":
        return list_monsters()
    if "monster_index" in data:
        return get_monster(str(data["monster_index"]))
    return jsonify({"error": "Invalid request"}), 400


# ------------- cache -------------

def cache_get(db, key: str):
    row = db.query(MonsterCache).filter(MonsterCache.key == key).first()
    if not row:
        return None
    if datetime.utcnow() - row.cached_at > CACHE_TTL:
        return None
    return row.payload


def cache_set(db, key: str, payload):
    rec = db.query(MonsterCache).filter(MonsterCache.key == key).first()
    if rec:
        rec.payload = payload
        rec.cached_at = datetime.utcnow()
    else:
        rec = MonsterCache(key=key, payload=payload)
        db.add(rec)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()


# ------------- endpoints -------------

def list_monsters():
    db = SessionLocal()
    try:
        key = "list"
        payload = cache_get(db, key)
        if not payload:
            r = requests.get(f"{UPSTREAM}/monsters", timeout=10)
            r.raise_for_status()
            payload = r.json()
            cache_set(db, key, payload)


        MonstersListSchema().load(payload)
        return jsonify(payload)
    except ValidationError as err:
        return jsonify({"error": "invalid upstream payload", "details": err.messages}), 502
    finally:
        db.close()


def get_monster(index: str):
    db = SessionLocal()
    try:
        key = f"monster:{index}"
        payload = cache_get(db, key)
        if not payload:
            r = requests.get(f"{UPSTREAM}/monsters/{index}", timeout=10)
            if r.status_code == 404:
                return jsonify({"error": "monster not found"}), 404
            r.raise_for_status()
            payload = r.json()
            cache_set(db, key, payload)


        MonsterDetailSchema().load(payload)
        return jsonify(payload)
    except ValidationError as err:
        return jsonify({"error": "invalid upstream payload", "details": err.messages}), 502
    finally:
        db.close()