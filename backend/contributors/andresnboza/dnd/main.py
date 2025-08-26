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
    return jsonify({'count': len(monsters), 'monsters': [monster.name for monster in monsters]})

# POST endpoint for monster list
@app.route('/monsters', methods=['POST'])
def monsters_list():
    try:
        req_data = request.get_json()
        # Expecting: {"resource": "monsters"}
        if req_data.get("resource") == "monsters":
            handler = FetchMonsterListHandler()
            result = handler.handle(req_data)
            return jsonify(result)
        return jsonify({"error": "Invalid payload"}), 400
    except Exception as e:
        log_message(f"Exception in /monsters: {e}")
        return jsonify({"error": "Internal server error"}), 500

# POST endpoint for get monster by index
@app.route('/monster', methods=['POST'])
def monster_get():
    req_data = request.get_json()
    # Expecting: {"monster_index": "<index>"}
    if "monster_index" in req_data:
        handler = FetchMonsterHandler()
        result = handler.handle(req_data)
        if 'status_code' in result:
            return jsonify(result), result['status_code']
        return jsonify(result)
    return jsonify({"error": "Invalid payload"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
