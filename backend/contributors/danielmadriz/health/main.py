import os
import sys
from flask import Flask, jsonify
from app.people_service import find_people
from app.people_extras import get_sushi_ramen_count, get_avg_weight_above_70_by_hair_color, get_most_common_food_overall, get_avg_weight_by_nationality_hair_color, get_top_oldest_people_per_nationality, get_top_people_by_hobbies, get_avg_height_nationality_general
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from database import get_session
from pathlib import Path

sys.path.append(os.path.dirname(__file__))

app = Flask(__name__)

@app.route('/')
def health():
    return {'status': 'ok'}

@app.route('/people/find', methods=['GET'])
def find_people_endpoint():
    try:
        session = get_session()
        people = find_people(session)
        
        response_data = {
            "success": True,
            "data": {
                "total": len(people),
                "results": [person.full_name for person in people]
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "data": {
                "total": 0,
                "results": []
            }
        }
        return jsonify(error_response), 500

@app.route('/people/sushi_ramen', methods=['GET'])
def people_sushi_ramen():
    try:
        session = get_session()
        count = get_sushi_ramen_count(session)
        
        response_data = {
            "success": True,
            "data": count
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "data": 0
        }
        return jsonify(error_response), 500

@app.route('/people/avg_weight_above_70_hair', methods=['GET'])
def people_avg_weight_above_70_hair():
    try:
        session = get_session()
        result = get_avg_weight_above_70_by_hair_color(session)
        
        response_data = {
            "success": True,
            "data": result
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "data": {}
        }
        return jsonify(error_response), 500

@app.route('/people/most_common_food_overall', methods=['GET'])
def people_most_common_food_overall():
    try:
        session = get_session()
        result = get_most_common_food_overall(session)
        
        response_data = {
            "success": True,
            "data": result
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "data": ""
        }
        return jsonify(error_response), 500

@app.route('/people/avg_weight_nationality_hair', methods=['GET'])
def people_avg_weight_nationality_hair():
    try:
        session = get_session()
        result = get_avg_weight_by_nationality_hair_color(session)
        
        response_data = {
            "success": True,
            "data": result
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "data": {}
        }
        return jsonify(error_response), 500

@app.route('/people/top_oldest_nationality', methods=['GET'])
def people_top_oldest_nationality():
    try:
        session = get_session()
        result = get_top_oldest_people_per_nationality(session)
        
        response_data = {
            "success": True,
            "data": result
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "data": {}
        }
        return jsonify(error_response), 500

@app.route('/people/top_hobbies', methods=['GET'])
def people_top_hobbies():
    try:
        session = get_session()
        result = get_top_people_by_hobbies(session)
        
        response_data = {
            "success": True,
            "data": result
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "data": []
        }
        return jsonify(error_response), 500

@app.route('/people/avg_height_nationality_general', methods=['GET'])
def people_avg_height_nationality_general():
    try:
        session = get_session()
        result = get_avg_height_nationality_general(session)
        
        response_data = {
            "success": True,
            "data": result
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "data": {"general": 0, "nationalities": {}}
        }
        return jsonify(error_response), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
