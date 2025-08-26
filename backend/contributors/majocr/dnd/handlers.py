from flask import jsonify
from proxy import get_or_cache_monster, list_monsters

def get_monster_handler(payload):
    index = payload.get('monster_index')
    if not index:
        return {"error":"Missing 'monster_index' in payload."}
    return get_or_cache_monster(index)

def list_monsters_handler(payload):
    if not payload or payload.get('resource')!='monsters':
        return {"error":"Payload must contain {'resource': 'monsters'}"}
    try:
        return list_monsters()
    except Exception as error:
        print(f"[ERROR] Failed to list monsters: {str(error)}")
        return {"error": "Internal server error"}, 500
