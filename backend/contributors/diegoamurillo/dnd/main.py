from flask import Flask, request, jsonify
from marshmallow import Schema, fields, ValidationError, validates_schema

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from upsteam_service import UpstreamService
from cache_service import CacheService


app = Flask(__name__)
upstream_service = UpstreamService()
cache_service = CacheService(upstream_service=upstream_service)


# Marshmallow schema
class HandlerSchema(Schema):
    resource = fields.Str(required=False)
    monster_index = fields.Str(required=False)

    @validates_schema
    def validate_payload(self, data, **kwargs):
        if "resource" in data and data["resource"] == "monsters":
            return
        if "monster_index" in data:
            if not isinstance(data["monster_index"], str) or not data["monster_index"].strip():
                raise ValidationError({"monster_index": "Must be a non-empty string"})
            return
        raise ValidationError("Payload must contain either 'resource':'monsters' or 'monster_index'.")


@app.route('/handler', methods=['POST'])
def handler():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400

        # Validate using Marshmallow
        schema = HandlerSchema()
        validated_data = schema.load(data)

        if validated_data.get("resource") == "monsters":
            return list_monsters()
        elif "monster_index" in validated_data:
            return get_monster(validated_data["monster_index"])
        else:
            return jsonify({"error": "Invalid event payload"}), 400

    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def list_monsters():
    monsters_list = cache_service.get_monsters_list()
    return jsonify({'monsters': monsters_list})


def get_monster(monster_index):
    monster = cache_service.get_monster_by_index(monster_index)
    return jsonify({'monster': monster})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
