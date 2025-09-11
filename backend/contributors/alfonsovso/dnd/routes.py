from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from .schemas import (
    ListEventSchema, GetEventSchema,
    ListResponseSchema, MonsterIndexItemSchema, MonsterDetailSchema, ErrorSchema
)
from .services import list_monsters, get_monster

bp = Blueprint("dnd", __name__)

@bp.post("/list")
def list_handler():
    try:
        _ = ListEventSchema().load(request.get_json(force=True))
    except ValidationError as err:
        return jsonify(ErrorSchema().dump({"error": "Invalid request payload", "details": err.messages})), 400

    data = list_monsters()

    if isinstance(data, dict) and "results" in data:
        results = data.get("results", [])
        count   = data.get("count", len(results))
    else:
        results = data 
        count   = len(results)

    try:
        items = MonsterIndexItemSchema(many=True).load(results)
        resp  = ListResponseSchema().load({"count": count, "results": items})
        return jsonify(resp), 200
    except ValidationError as err:
        return jsonify(ErrorSchema().dump({"error": "Invalid list data", "details": err.messages})), 502


@bp.post("/get")
def get_handler():
    try:
        payload = GetEventSchema().load(request.get_json(force=True))
    except ValidationError as err:
        return jsonify(ErrorSchema().dump({"error": "Invalid request payload", "details": err.messages})), 400

    data = get_monster(payload["monster_index"])
    if isinstance(data, tuple):
        body, status = data
        if status >= 400:
            return jsonify(ErrorSchema().dump({"error": body.get("error", "Upstream error")})), status
        return jsonify(body), status

    try:
        monster = MonsterDetailSchema().load(data)
        return jsonify(monster), 200
    except ValidationError as err:
        return jsonify(ErrorSchema().dump({"error": "Invalid monster data", "details": err.messages})), 502
