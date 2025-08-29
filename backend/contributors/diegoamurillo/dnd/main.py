from flask import Flask, request, jsonify
from marshmallow import Schema, fields, ValidationError

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from upsteam_service import UpstreamService
from cache_service import CacheService


app = Flask(__name__)
upstream_service = UpstreamService()
cache_service = CacheService(upstream_service=upstream_service)

class ListSchema(Schema):
    pass


class GetSchema(Schema):
    monster_index = fields.Str(required=True)


@app.route('/list', methods=['GET'])
def list_monsters():
    try:
        schema = ListSchema()
        schema.load(request.args)

        monsters_list = cache_service.get_monsters_list()
        return jsonify({'monsters': monsters_list}), 200
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get/<monster_index>', methods=['GET'])
def get_monster(monster_index):
    try:
        schema = GetSchema()
        validated_data = schema.load({"monster_index": monster_index})

        monster = cache_service.get_monster_by_index(validated_data["monster_index"])
        if not monster:
            return jsonify({"error": f"Monster '{monster_index}' not found"}), 404

        return jsonify({'monster': monster}), 200
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
