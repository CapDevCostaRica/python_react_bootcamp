from flask import jsonify
from .proxy import get_or_cache_monster, list_monsters
from .schema import MonsterRequestSchema_majocr, MonstersListResourceSchema_majocr
from marshmallow import ValidationError

def get_monster_handler(payload):
    try:
        valiated = MonsterRequestSchema_majocr().load(payload)
        index = valiated['monster_index']
        return get_or_cache_monster(index)
    except ValidationError as error:
        print(f"[ERROR] Invalid payload for get_monster_handler: {str(error)}")
        return {"error":"Missing 'monster_index' in payload."}

def list_monsters_handler(payload):
    try:
        MonstersListResourceSchema_majocr().load(payload)
        return list_monsters()
    except ValidationError as error:
        print(f"[ERROR] Invalid payload for list_monsters_handler: {str(error)}")
        return {"error":"Payload must contain {'resource': 'monsters'}"}
    except Exception as error:
        print(f"[ERROR] Failed to list monsters: {str(error)}")
        response = jsonify({'error': str(error)})
        response.status_code = 500
        return response
