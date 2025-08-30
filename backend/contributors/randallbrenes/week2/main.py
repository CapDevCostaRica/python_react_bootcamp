from flask import Flask, jsonify, request
from marshmallow import ValidationError
from app.people_service import PeopleService
from app.schema import (
    WeightGroupSchema, RequestFindSchema, ResponseFindSchema,
    ResponseDictSchema, ResponseStringGroupSchema, ResponseListSchema
)

app = Flask(__name__)

find_schema = RequestFindSchema()
response_find_schema = ResponseFindSchema()
weight_schema = WeightGroupSchema()
dict_response_schema = ResponseDictSchema()
string_response_schema = ResponseStringGroupSchema()
list_response_schema = ResponseListSchema()
people_service = PeopleService()

def field_value(value: str):
    if value.isdigit():
        return int(value)
    try:
        return float(value)
    except ValueError:
        pass
    if value.lower() in ["true", "false"]:
        return value.lower() == "true"
    return value

def parse_query_string(args):
    result = { "filters": {} }
    for key, value in args.items():
        # 8:-1 remove filters[] string
        field_name = key[8:-1].replace('"', "").replace("'", "")
        result["filters"][field_name] = field_value(value)
    return result

def execute_service(service_method, input_data=None, response_schema=None):
    try:
        if input_data is not None:
            response = service_method(input_data)
        else:
            response = service_method()

        if response_schema:
            response_schema.load(response)

    except ValidationError as err:
        response = {"success": False, "message": err.messages, "code": 400}
    except Exception as e:
        response = {"success": False, "message": str(e), "code": 500}

    return jsonify(response), response.get('code', 500)

@app.route('/')
def health():
    return {"status": "ok"}

@app.route('/people/find', methods=['GET'])
def find():
    query_string = request.args.to_dict()
    body = parse_query_string(query_string)
    data, err = None, None
    try:
        data = find_schema.load(body)
    except ValidationError as err:
        return jsonify({"success": False, "message": err.messages, "code": 400}), 400

    return execute_service(people_service.find, input_data=data, response_schema=response_find_schema)

@app.route('/people/sushi_ramen')
def sushi_ramen():
    filters = [{"food": "sushi"}, {"food": "ramen"}]
    return execute_service(people_service.find, input_data={"filters": filters}, response_schema=response_find_schema)

@app.route('/people/avg_weight_above_70_hair', methods=['GET'])
def avg_weight_above_hair():
    body = None
    weight = 70
    if len(request.args):
        query_string = request.args.to_dict()
        body = parse_query_string(query_string)
    try:
        if body:
            data = weight_schema.load(body)
            weight = data.get('filters', {}).get('weight', 70)
    except ValidationError as err:
        return jsonify({"success": False, "message": err.messages, "code": 400}), 400

    return execute_service(people_service.avg_weight_above_hair, input_data=weight, response_schema=dict_response_schema)

@app.route('/people/most_common_food_overall')
def most_common_food_overall():
    return execute_service(people_service.extra1, response_schema=string_response_schema, input_data=None)

@app.route('/people/avg_weight_nationality_hair')
def avg_weight_nationality_hair():
    return execute_service(people_service.extra2, response_schema=dict_response_schema)

@app.route('/people/top_oldest_nationality')
def top_oldest_nationality():
    return execute_service(people_service.extra3, response_schema=dict_response_schema)

@app.route('/people/top_hobbies')
def top_hobbies():
    return execute_service(people_service.extra4, response_schema=list_response_schema)

@app.route('/people/avg_height_nationality_general')
def avg_height_nationality_general():
    return execute_service(people_service.extra5, response_schema=dict_response_schema)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
