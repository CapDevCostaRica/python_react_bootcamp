from flask import Blueprint, request, jsonify
from app.services.monster_service import get_all_monsters, get_monster_by_index, fetch_monsters_from_api, bulk_insert_monsters, fetch_monster_details_from_api, insert_monster_details
from app.schemas.index import MonsterRequestSchema, MonsterListRequestSchema, MonsterListResponseModelSchema, DetailedMonsterSchema, MonsterDetailResponseSchema
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
            print("🚀Database Updated🚀", flush=True)

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
            monster_data = fetch_monster_details_from_api(monster_index)
            if monster_data is None:
                return jsonify({'error': 'Monster not found'}), 404
            schema = MonsterDetailResponseSchema()
            monster = schema.load(monster_data)
            insert_monster_details(monster)
            print("🚀Database Updated🚀", flush=True)

        return jsonify(monster)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
