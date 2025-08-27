from flask import Flask, request as flask_request, jsonify
import os, sys

# --- Rutas para acceder al framework ---
CURR_DIR = os.path.dirname(__file__)                 # .../contributors/odkeyo/dnd
ROOT_DIR = os.path.abspath(os.path.join(CURR_DIR, '..', '..', '..'))   # .../backend
FRAMEWORK_DIR = os.path.join(ROOT_DIR, 'framework')  # .../backend/framework

for p in (CURR_DIR, ROOT_DIR, FRAMEWORK_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# --- Imports del framework (DB y modelos) ---
from database import get_session
from marshmallow import ValidationError
from models import odkeyo_Monster, odkeyo_MonsterDetail

# --- Imports locales del módulo dnd ---
from schemas import (
    ListInputSchema, GetInputSchema,
    odkeyo_MonsterListSchema, odkeyo_MonsterDetailSchema,
)
from clients import odkeyo_DnDClient, odkeyo_UpstreamError
from service import odkeyo_MonsterProxyService

app = Flask(__name__)

client = odkeyo_DnDClient()
service = odkeyo_MonsterProxyService(client)

list_in  = ListInputSchema()
get_in   = GetInputSchema()
list_out = odkeyo_MonsterListSchema()
det_out  = odkeyo_MonsterDetailSchema()

@app.post("/list")
def list_handler():
    try:
        payload = list_in.load(flask_request.get_json(force=True))
        session = get_session()
        try:
            results = service.list_monsters(session)
            session.commit()
            return jsonify(list_out.dump({"count": len(results), "results": results})), 200
        finally:
            session.close()
    except odkeyo_UpstreamError as e:
        return jsonify({"error": "upstream_failed", "detail": str(e)}), 502
    except ValidationError as ve:
        return jsonify({"error": ve.messages}), 400

@app.post("/get")
def get_handler():
    try:
        payload = get_in.load(flask_request.get_json(force=True))
        session = get_session()
        try:
            data = service.get_monster(session, payload["monster_index"])
            session.commit()
            return jsonify(det_out.dump(data)), 200
        finally:
            session.close()
    except odkeyo_UpstreamError as e:
        return jsonify({"error": "upstream_failed", "detail": str(e)}), 502
    except ValidationError as ve:
        return jsonify({"error": ve.messages}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 4000)))
