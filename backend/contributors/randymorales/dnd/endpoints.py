from flask.views import MethodView
from flask import request, jsonify
from marshmallow import ValidationError
from schemas import (
    RandymoralesMonsterListInputSchema,
    RandymoralesMonsterGetInputSchema,
    RandymoralesMonsterListOutputSchema,
    RandymoralesMonsterGetOutputSchema,
)
from service import RandymoralesMonsterProxyService
service = RandymoralesMonsterProxyService()

class MonsterListAPI(MethodView):
    """POST /list: List all monsters."""
    def post(self):
        try:
            data = request.get_json()
            input_data = RandymoralesMonsterListInputSchema().load(data)
        except ValidationError as err:
            return jsonify({'error': err.messages}), 400
        if input_data['resource'] != 'monsters':
            return jsonify({'error': 'Invalid resource'}), 400
        try:
            result = service.get_monster_list()
        except RuntimeError:
            return jsonify({'error': 'Upstream error'}), 502
        try:
            RandymoralesMonsterListOutputSchema().load(result)
        except ValidationError as err:
            return jsonify({'error': 'Invalid upstream data', 'details': err.messages}), 502
        return jsonify(result)

class MonsterGetAPI(MethodView):
    """POST /get: Get a monster by index."""
    def post(self):
        try:
            data = request.get_json()
            input_data = RandymoralesMonsterGetInputSchema().load(data)
        except ValidationError as err:
            return jsonify({'error': err.messages}), 400
        monster_index = input_data['monster_index']
        try:
            result = service.get_monster(monster_index)
        except RuntimeError:
            return jsonify({'error': 'Upstream error'}), 502
        try:
            RandymoralesMonsterGetOutputSchema().load(result)
        except ValidationError as err:
            return jsonify({'error': 'Invalid upstream data', 'details': err.messages}), 502
        return jsonify(result)
