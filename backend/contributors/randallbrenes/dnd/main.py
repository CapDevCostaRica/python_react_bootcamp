from flask import Flask, jsonify, request
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from database import get_session
from monsters import Monsters

app = Flask(__name__)

@app.route("/", methods=["POST"])
def post_get_data():
    session = get_session()
    data = request.get_json()
    is_getting_all_monsters = "resource" in data and data["resource"] == "monsters"
    is_getting_single_monster = "monster_index" in data
    valid_request = is_getting_all_monsters or is_getting_single_monster
    response_code = 400
    response = {"error": "invalid request"}
    if valid_request:
        response_code = 200
        response = []

        if is_getting_all_monsters:
            response = Monsters(session).get_all()

        elif is_getting_single_monster:
            response = response = Monsters(session).get_single(data["monster_index"])

            if not response:
                response = {"error": "Monster not found"}
                response_code = 404

    return jsonify(response), response_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
