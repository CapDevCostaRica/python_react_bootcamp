import os
import sys
from flask import Flask, jsonify
from app.people_service import find_people
from app.people_extras import get_sushi_ramen_count
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
