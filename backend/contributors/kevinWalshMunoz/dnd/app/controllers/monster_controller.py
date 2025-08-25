from flask import Blueprint, request, jsonify
from app.services.monster_service import get_all_monsters, get_monster_by_index, fetch_monsters_from_api, bulk_insert_monsters
from app.schemas.index import MonsterRequestSchema, MonsterListRequestSchema, MonsterListResponseModelSchema
from marshmallow import ValidationError

bp = Blueprint('monsters', __name__, url_prefix='/monsters')

@bp.route('/list', methods=['POST'])
def list_monsters():
    try:
        schema = MonsterListRequestSchema()
        schema.load(request.get_json() or {})
        
        monsters = get_all_monsters()
        model_schema = MonsterListResponseModelSchema()
        result = model_schema.dump(monsters)

        if result['count'] == 0:
            result = fetch_monsters_from_api()
            bulk_insert_monsters(result)

        return jsonify(result)
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
        
        model_schema = MonsterModelSchema()
        result = model_schema.dump(monster)
        
        return jsonify({'Monster': result})
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
