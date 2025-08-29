from flask import Flask, request as flask_request, jsonify
import os, sys

CURR_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(CURR_DIR, '..', '..', '..'))
FRAMEWORK_DIR = os.path.join(ROOT_DIR, 'framework')

for p in (CURR_DIR, ROOT_DIR, FRAMEWORK_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from database import get_session
from marshmallow import ValidationError
from models import odkeyo_Monster, odkeyo_MonsterDetail

from schemas import (
    ListInputSchema, GetInputSchema,
    odkeyo_MonsterListSchema,
    MonsterDetailDataSchema,
)
from clients import odkeyo_DnDClient, odkeyo_UpstreamError
from service import odkeyo_MonsterProxyService

app = Flask(__name__)

client = odkeyo_DnDClient()
service = odkeyo_MonsterProxyService(client)

list_in   = ListInputSchema()
get_in    = GetInputSchema()
list_out  = odkeyo_MonsterListSchema()
det_check = MonsterDetailDataSchema()

@app.post("/list")
def list_handler():
    try:
        list_in.load(flask_request.get_json(force=True))
        session = get_session()
        try:
            results = service.list_monsters(session)
            session.commit()
            
            payload = {"count": len(results), "results": results}
            return jsonify(list_out.dump(payload)), 200
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

            data_dict = data if isinstance(data, dict) else getattr(data, "data", data)

            det_check.load(data_dict)
            clean = dict(data_dict)
            clean.pop("updated_at", None) 
            return jsonify(clean), 200
        finally:
            session.close()
    except odkeyo_UpstreamError as e:
        return jsonify({"error": "upstream_failed", "detail": str(e)}), 502
    except ValidationError as ve:
        return jsonify({"error": ve.messages}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 4000)))
