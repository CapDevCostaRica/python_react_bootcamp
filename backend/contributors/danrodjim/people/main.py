from flask import Flask, request, jsonify, make_response
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from validators import FindPersonRequestValidator, PersonSchema
import json
import db_service as db

app = Flask(__name__)

@app.route('/')
def health():
    return {'status': 'ok'}


@app.route('/people/find', methods=['GET'])
def find_people():
    if not request.args:
        return jsonify({"message": "What are you looking for?"})
    
    filters = {}
    for filter in request.args:
        filters[filter[8:-1]] = request.args[filter]
    
    schema = FindPersonRequestValidator()
    validation = schema.load(filters)

    result = db.find_person(validation)

    people_schema = PersonSchema(many=True)
    people_found = people_schema.dump(result)

    response = []

    for person in people_found:
        response.append(person["name"])
    
    return jsonify({
    "success": True, 
    "data": {
        "total": len(response),
        "results": response
    }
})

@app.route('/people/sushi_ramen', methods=['GET'])
def sushi_ramen():
    result = db.find_sushi_ramen()
    return jsonify({"success": True, "data": len(result)})

@app.route('/people/avg_weight_above_70_hair', methods=['GET'])
def avg_weight_above_70_hair():
    result = db.find_avg_weight_above_70_hair()
    return jsonify({"success": True, "data": result})

@app.route('/people/most_common_food_overall', methods=['GET'])
def most_common_food_overall():
    result = db.find_most_common_food()
    # result = db.find_most_common_food_by_file()
    return jsonify({"success": True, "data": result[0]})

@app.route('/people/avg_weight_nationality_hair', methods=['GET'])
def avg_weight_nationality_hair():
    result = db.find_avg_weight_nationality_hair()
    response = {}
    for r in result:
        key = r[0]+"-"+r[1]
        value = round(float(r[2]), 2)
        response[key] = value
    print(response)
    return jsonify({"success": True, "data": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
