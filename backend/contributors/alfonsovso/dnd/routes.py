from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from .schemas import ListEventSchema, GetEventSchema
from .services import list_monsters, get_monster

bp = Blueprint("dnd", __name__)

@bp.post("/list")
def list_handler():
    try:
        payload = ListEventSchema().load(request.get_json(force=True))
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    data = list_monsters()
    return jsonify({"results": data}), 200

@bp.post("/get")
def get_handler():
    try:
        payload = GetEventSchema().load(request.get_json(force=True))
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    data = get_monster(payload["monster_index"])
    if isinstance(data, tuple):
        body, status = data
        return jsonify(body), status
    return jsonify(data), 200
