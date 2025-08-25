from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import requests
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from contributors.Luch1f3rchoCR.dnd.db import Base, engine, SessionLocal
from contributors.Luch1f3rchoCR.dnd.models import MonsterCache
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
      - {"monster_index": <string>}   -> get monster by index
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

def cache_get(db, key):
    row = db.query(MonsterCache).filter(MonsterCache.key == key).first()
    if not row:
        return None
    if datetime.utcnow() - row.cached_at > CACHE_TTL:
        return None
    return row.payload

def cache_set(db, key, payload):
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

def list_monsters():
    db = SessionLocal()
    try:
        key = "list"
        payload = cache_get(db, key)
        source = "cache" if payload else "upstream"
        if not payload:
            r = requests.get(f"{UPSTREAM}/monsters", timeout=10)
            r.raise_for_status()
            payload = r.json()
            cache_set(db, key, payload)

        try:
            MonstersListSchema().load(payload)
        except ValidationError as err:
            return jsonify({"error": "invalid upstream payload", "details": err.messages}), 502

        return jsonify({"source": source, **payload})
    finally:
        db.close()

def get_monster(index: str):
    db = SessionLocal()
    try:
        key = f"monster:{index}"
        payload = cache_get(db, key)
        source = "cache" if payload else "upstream"
        if not payload:
            r = requests.get(f"{UPSTREAM}/monsters/{index}", timeout=10)
            if r.status_code == 404:
                return jsonify({"error": "monster not found"}), 404
            r.raise_for_status()
            payload = r.json()
            cache_set(db, key, payload)

        try:
            MonsterDetailSchema().load(payload)
        except ValidationError as err:
            return jsonify({"error": "invalid upstream payload", "details": err.messages}), 502

        return jsonify({"source": source, **payload})
    finally:
        db.close()