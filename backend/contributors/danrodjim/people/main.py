from flask import Flask, request, jsonify, make_response
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from validators import FindPersonRequestValidator, PersonSchema
from collections import defaultdict
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
    try:
        result = db.find_sushi_ramen()
    except Exception as err:
        return jsonify({"message": str(err)}), 500
    return jsonify({"success": True, "data": len(result)})

@app.route('/people/avg_weight_above_70_hair', methods=['GET'])
def avg_weight_above_70_hair():
    try:
        result = db.find_avg_weight_above_70_hair()
    except Exception as err:
        return jsonify({"message": str(err)}), 500
    return jsonify({"success": True, "data": result})

@app.route('/people/most_common_food_overall', methods=['GET'])
def most_common_food_overall():
    try:
        result = db.find_most_common_food()
        # result = db.find_most_common_food_by_file()
    except Exception as err:
        return jsonify({"message": str(err)}), 500
    return jsonify({"success": True, "data": result[0]})

@app.route('/people/avg_weight_nationality_hair', methods=['GET'])
def avg_weight_nationality_hair():
    try:
        result = db.find_avg_weight_nationality_hair()
    except Exception as err:
        return jsonify({"message": str(err)}), 500
    response = {}
    for r in result:
        key = r[0]+"-"+r[1]
        value = round(float(r[2]), 2)
        response[key] = value
    return jsonify({"success": True, "data": response})

@app.route('/people/top_oldest_nationality', methods=['GET'])
def top_oldest_nationality():
    try:
        result = db.find_top_oldest_nationality()
    except Exception as err:
        return jsonify({"message": str(err)}), 500
    grouped = defaultdict(list)
    for person in result:
        grouped[person.nationality].append(person.name)
    data = dict(grouped)
    return jsonify({"success": True, "data": data})

@app.route('/people/top_hobbies', methods=['GET'])
def top_hobbies():
    try:
        result = db.find_top_hobbies()
    except Exception as err:
        return jsonify({"message": str(err)}), 500
    return jsonify({"success": True, "data": result})

@app.route('/people/avg_height_nationality_general', methods=['GET'])
def avg_height_nationality_general():
    try:
        result = db.find_avg_height_nationality_general()
    except Exception as err:
        return jsonify({"message": str(err)}), 500
    return jsonify({"success": True, "data": result})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
