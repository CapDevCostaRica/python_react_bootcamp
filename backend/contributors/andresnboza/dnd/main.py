from flask import Flask, jsonify, request

import random

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database import get_session
from models import AndresnbozaMonster
from utils.logger import log_message

# Import Marshmallow schemas and handlers
from handler.fetch_monster_handler import FetchMonsterHandler
from handler.fetch_monster_list_handler import FetchMonsterListHandler

from schemas.monster_response_schema import MonsterResponseSchema

app = Flask(__name__)

@app.route('/random')
def get_random_monster():
    session = get_session()
    monsters = session.query(AndresnbozaMonster).all()
    session.close()
    if not monsters:
        return jsonify({'error': 'No andresnboza dnd monsters found.'}), 404
    monster = random.choice(monsters).name
    return jsonify({'monster': monster})

@app.route('/all')
def get_all_monster():
    session = get_session()
    monsters = session.query(AndresnbozaMonster).all()
    session.close()
    if not monsters:
        return jsonify({'error': 'No andresnboza dnd monsters found.'}), 404
    schema = MonsterResponseSchema(many=True)
    result = schema.dump([monster.to_dict() for monster in monsters])
    return jsonify({'count': len(result), 'results': result})

# POST endpoint for monster list
@app.route('/list', methods=['POST'])
def monsters_list():
    try:
        req_data = request.get_json()
        # Expecting: {"resource": "monsters"}
        if req_data.get("resource") == "monsters":
            handler = FetchMonsterListHandler()
            result = handler.handle(req_data)
            # Use MonsterSummarySchema for validating summary list from external API
            from schemas.monster_summary_schema import MonsterSummarySchema
            monsters = result.get('results', []) if isinstance(result, dict) and 'results' in result else result
            schema = MonsterSummarySchema(many=True)
            validated = schema.dump(monsters)
            count = result.get('count', len(validated)) if isinstance(result, dict) else len(validated)
            return jsonify({'count': count, 'results': validated})
        return jsonify({"error": "Invalid payload"}), 400
    except Exception as e:
        log_message(f"Exception in /monsters: {e}")
        return jsonify({"error": "Internal server error"}), 500

# POST endpoint for get monster by index
@app.route('/get', methods=['POST'])
def monster_get():
    req_data = request.get_json()
    # Expecting: {"monster_index": "<index>"}
    if "monster_index" in req_data:
        handler = FetchMonsterHandler()
        result = handler.handle(req_data)
        from schemas.monster_response_schema import MonsterResponseSchema
        schema = MonsterResponseSchema()
        # If result is a dict with monster data, validate and serialize
        if 'status_code' in result:
            return jsonify(result), result['status_code']
        if 'monster' in result and isinstance(result['monster'], dict):
            validated = schema.dump(result['monster'])
            return jsonify({'monster': validated, 'source': result.get('source')})
        return jsonify(result)
    return jsonify({"error": "Invalid payload"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
