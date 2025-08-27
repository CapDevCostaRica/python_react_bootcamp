from flask import Flask, jsonify, request, make_response
import os
import sys
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from datetime import datetime, timedelta
from marshmallow import ValidationError
from validators import ListMonsterResponseSchema, GetMonsterResponseSchema, GetMonsterRequestSchema, ListMonsterRequestSchema

import db_service as db

app = Flask(__name__)

last_call = None
URL = "https://www.dnd5eapi.co/api/2014/monsters"
payload = {}
headers = { 'Accept': 'application/json' }

@app.route('/list', methods=['POST'])
def list_of_monsters():
    ## Validating the request
    schema = ListMonsterRequestSchema()
    try:
        schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    ## Always the first call will get the list of monsters from the dnd API
    ## And it will be checking if 5 minutes have passed since last call (this is so that it behaves like a cache)
    global last_call
    now = datetime.now()

    if last_call is None or now - last_call >= timedelta(minutes=5):
        try:
            dnd_api_response = requests.request("GET", URL, headers=headers, data=payload)

            schema = ListMonsterResponseSchema(many=True)
            schema.dump(dnd_api_response)

            last_call = now

            response_data = dnd_api_response.json()
            response = make_response(jsonify(response_data))

            @response.call_on_close
            def update_db():
                db.update_database_monsters_list(response_data["results"])

            return response
            
        except Exception as err:
            return jsonify({"message": str(err)}), 500
    else:
        ## If 5 minutes have not passed then get the list from the database
        monsters_list = db.get_monsters_list()
        if not monsters_list:
            return jsonify({'error': 'No monsters found.'}), 404
        
        schema = ListMonsterResponseSchema(many=True)
        result = schema.dump(monsters_list)

        return jsonify({"count": len(result), "results": sorted(result, key=lambda x: x['index'])}), 200


@app.route('/get', methods=['POST'])
def get_monster():
    ## Validating the request
    schema = GetMonsterRequestSchema()
    try:
        schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    data = request.get_json()
    monster_get = db.get_monster(data["monster_index"])

    if not monster_get:
        dnd_api_response = requests.request("GET", URL+"/"+data["monster_index"], headers=headers, data=payload)
        if dnd_api_response:
            api_to_json = dnd_api_response.json()
            schema = GetMonsterResponseSchema(raw_data=api_to_json)
            schema.dump(api_to_json)
            response_data = api_to_json
            response = make_response(jsonify(response_data))
            @response.call_on_close
            def update_db():
                db.update_database_monsters_get(response_data)
            return response
        return jsonify({'error': 'No monsters found.'}), 404
    else:
        raw_data = monster_get.data or {}
        schema = GetMonsterResponseSchema(raw_data=raw_data)
        schema.dump(raw_data)
        if not monster_get.data or monster_get.data == {}:
            dnd_api_response = requests.request("GET", URL+"/"+data["monster_index"], headers=headers, data=payload)
            api_to_json = dnd_api_response.json()
            schema = GetMonsterResponseSchema(raw_data=api_to_json)
            schema.dump(api_to_json)

            response_data = api_to_json
            response = make_response(jsonify(response_data))

            @response.call_on_close
            def update_db():
                db.update_database_monsters_get(response_data)

            return response
        else:
            schema = GetMonsterResponseSchema(raw_data=raw_data)
            result = schema.dump(raw_data)
            response = make_response(result)

            @response.call_on_close
            def update_db():
                dnd_api_response = requests.request("GET", URL+"/"+data["monster_index"], headers=headers, data=payload)
                api_to_json = dnd_api_response.json()
                schema = GetMonsterResponseSchema(raw_data=api_to_json)
                schema.dump(api_to_json)
                response_data = api_to_json
                db.update_database_monsters_get(response_data)

            return response
            

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
