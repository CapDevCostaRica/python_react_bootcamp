import os
import sys
from flask import Flask, jsonify, request
from marshmallow import ValidationError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from database import get_session
from schemas.request import RequestAllSchema, RequestSingleSchema
from schemas.response import Response
from monsters import Monsters

app = Flask(__name__)
request_all_schema = RequestAllSchema()
request_one_schema = RequestSingleSchema()
response_validation = Response()

@app.route("/get", methods=["POST"])
def post_get_single_data():
    try:
        body = request.get_json(force=True)
        data = request_one_schema.load(body)
        try:
            db = get_session()
            monster_data = Monsters(db).get_single(data["monster_index"])
            if monster_data is not None:
                response = {"monster": monster_data, "code": 200}
            else:
                response = {"error": "Monster " + data["monster_index"] + " not found", "code": 404}        
            db.close()
        except Exception as e:
            response = {"error": str(e), "code": 500}
    except ValidationError as err:
        response = {"error": err.messages, "code": 400}
    except Exception as x:
        response = {"error": str(x), "code": 500}

    try:
        validated_response = response_validation.load(response)
        response_code = validated_response["code"] if "code" in validated_response else 500
        response = validated_response["monster"]["json_data"] if "monster" in validated_response else validated_response["error"]
    except ValidationError as err:
        response_code = 400
        response = err.messages
    return jsonify(response), response_code

@app.route("/list", methods=["POST"])
def post_list_all_data():
    try:
        body = request.get_json(force=True)
        request_all_schema.load(body)
        try:
            db = get_session()
            response = {"list": Monsters(db).get_all(), "code": 200}
            db.close()
        except Exception as e:
            response =  {"error": str(e), "code": 500}
    except ValidationError as err:
        response = {"error": err.messages, "code": 400}
    except Exception as x:
        response = {"error": str(x), "code": 500}
    try:
        validated_response = response_validation.load(response)
        response_code = validated_response["code"] if "code" in validated_response else 500
        response = validated_response["list"] if "list" in validated_response else validated_response["error"]
    except ValidationError as err:
        response = err.messages
        response_code = 400
    return jsonify(response), response_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
