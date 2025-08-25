from flask import Blueprint, request, jsonify
from app.services.monster_service import get_all_monsters, get_monster_by_index
from app.schemas.index import MonsterRequestSchema, MonsterListRequestSchema
from marshmallow import ValidationError

bp = Blueprint('monsters', __name__, url_prefix='/monsters')

@bp.route('/list', methods=['POST'])
def list_monsters():
    try:
        schema = MonsterListRequestSchema()
        schema.load(request.get_json() or {})
        
        return jsonify({'Monsters': get_all_monsters()})
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400

@bp.route('/get', methods=['POST'])
def get_monster():
    try:
        schema = MonsterRequestSchema()
        data = schema.load(request.get_json() or {})
        
        monster_index = data['monster_index']
        
        monster = get_monster_by_index(monster_index)
        if not monster:
            return jsonify({'error': 'Monster not found'}), 404
        
        return jsonify({'Monster': monster})
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
