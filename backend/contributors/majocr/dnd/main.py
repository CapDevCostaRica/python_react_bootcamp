from flask import Flask, request, jsonify
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../majocr/dnd')))
from handlers import get_monster_handler, list_monsters_handler

app = Flask(__name__)

@app.route('/')
def health():
    return {'status': 'ok'}

@app.route('/monsters/list', methods=['POST'])
def list_monsters():
    payload = request.get_json()
    try:
        result = list_monsters_handler(payload)
        return jsonify(result), 200
    except Exception as error:
        return jsonify({'error': str(error)}), 400


@app.route('/monsters/get', methods=['POST'])
def get_monster():
    payload = request.get_json()
    try:
        result = get_monster_handler(payload)
        return jsonify(result), 200
    except Exception as error:
        return jsonify({'error': str(error)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)