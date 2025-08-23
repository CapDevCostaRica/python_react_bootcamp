from flask import jsonify
from proxy import get_or_cache_monster, list_cached_monsters

def get_monster_handler(payload):
    index = payload.get('monster_index')
    if not index:
        return jsonify({"error":"Missing 'monster_index' in payload."})
    return get_or_cache_monster(index)

def list_monsters_handler(payload):
    try:
        return list_cached_monsters(), 200
    except Exception as error:
        print(f"[ERROR] Failed to list monsters: {str(error)}")
        return jsonify({"error": "Internal server error"}), 500
