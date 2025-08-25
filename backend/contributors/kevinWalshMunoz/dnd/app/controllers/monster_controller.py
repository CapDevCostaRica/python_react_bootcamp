from flask import Blueprint, request, jsonify
from app.services.monster_service import get_all_monsters, get_monster_by_index

bp = Blueprint('monsters', __name__, url_prefix='/monsters')

@bp.route('/list', methods=['POST'])
def list_monsters():
    return jsonify({'Monsters': get_all_monsters()})

@bp.route('/get', methods=['POST'])
def get_monster():
    data = request.get_json()
    monster_index = data.get('monster_index') if data else None
    if not monster_index:
        return jsonify({'error': 'Se requiere el parámetro monster_index'}), 400
    
    monster = get_monster_by_index(monster_index)
    if not monster:
        return jsonify({'error': 'Monstruo no encontrado'}), 404
    
    return jsonify({'Monster': monster})
