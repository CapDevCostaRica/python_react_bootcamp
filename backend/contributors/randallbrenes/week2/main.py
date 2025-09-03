from flask import Flask, jsonify, request
from marshmallow import ValidationError
from app.people_service import PeopleService
from app.schema import (
    WeightGroupSchema, RequestFindSchema, ResponseFindSchema,
    ResponseDictSchema, ResponseStringGroupSchema, ResponseListSchema,
    ResponseIntGroupSchema
)
from app.helpers import execute_service, parse_query_string

app = Flask(__name__)

find_schema = RequestFindSchema()
response_find_schema = ResponseFindSchema()
weight_schema = WeightGroupSchema()
dict_response_schema = ResponseDictSchema()
string_response_schema = ResponseStringGroupSchema()
list_response_schema = ResponseListSchema()
people_service = PeopleService()
response_sushi_ramen_schema = ResponseIntGroupSchema()

@app.route('/')
def health():
    return {"status": "ok"}

@app.route('/people/find', methods=['GET'])
def find():
    query_string = request.args.to_dict()
    body = parse_query_string(query_string)
    return execute_service(people_service.find, input_data=body, response_schema=response_find_schema, input_schema=find_schema)

@app.route('/people/sushi_ramen')
def sushi_ramen():
    filters = [{"food": "sushi"}, {"food": "ramen"}]
    return execute_service(people_service.sushi_ramen, input_data={"filters": filters}, response_schema=response_sushi_ramen_schema)

@app.route('/people/avg_weight_above_70_hair', methods=['GET'])
def avg_weight_above_hair():
    return execute_service(people_service.avg_weight_above_hair, input_data=70, response_schema=dict_response_schema)

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
