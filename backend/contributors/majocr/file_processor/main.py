import os
import sys
from flask import Flask, jsonify, request

from app.service import avg_height_nationality_general, get_avg_weight_above_70_by_hair, get_avg_weight_by_nationality_and_hair, get_most_common_food, get_people_like_shushi_and_ramen, get_top_oldest_natuinality, query_people_by_filters, top_hobbies
from app.schema import PeopleResponseSchema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from app.config.seed_config import get_seed_config
from database import get_session
from pathlib import Path

app = Flask(__name__)
base_path = Path(__file__).resolve().parent

def get_csv_path(filename):
    #print (f"Base path: {base_path}")
    csv_path = base_path / "files" / filename
    resolved_path = csv_path.resolve()
    print(f"Path: {resolved_path}")
    return resolved_path


people_csv_path = get_csv_path("people_data.csv")
physical_csv_path = get_csv_path("physical_data.csv")
foods_csv_path = get_csv_path("favorite_data.csv")
hobbies_csv_path = get_csv_path("hobbies_data.csv")
studies_csv_path = get_csv_path("studies_data.csv")
family_csv_path = get_csv_path("family_data.csv")

csv_paths = {
    "people": people_csv_path,
    "physical": physical_csv_path,
    "foods": foods_csv_path,
    "hobbies": hobbies_csv_path,
    "studies": studies_csv_path,
    "family": family_csv_path
}

SEED_CONFIG = get_seed_config(csv_paths)

def seed_if_needed(session, name, config):
    if config["check"](session):
        print(f"{name} already seeded.")
    else:
        print(f"Seeding {name}...")
        config["seed"](session, *config["args"])
        print(f"{name} seeded.")
        
def is_data_seeded(session):
    for name, config in SEED_CONFIG.items():
        seed_if_needed(session, name, config)

@app.route('/')
def health():
    return {'status': 'here_ok'}

def extract_filters(args):
    filters = {}
    for key, value in args.items():
        if key.startswith('filters[') and key.endswith(']'):
            filter_key = key[len('filters['):-1]
            filters[filter_key] = value
    if 'age' in filters:
        try:
            filters['age'] = int(filters['age'])
        except ValueError:
            print(f"Invalid age value: {filters['age']}. It should be an integer.")
            filters.pop('age')
    if 'height_cm' in filters:
        try:
            filters['height_cm'] = float(filters['height_cm'])
        except ValueError:
            print(f"Invalid height_cm value: {filters['height_cm']}. It should be a float.")
            filters.pop('height_cm')
    if 'weight_kg' in filters:
        try:
            filters['weight_kg'] = float(filters['weight_kg'])
        except ValueError:
            print(f"Invalid weight_kg value: {filters['weight_kg']}. It should be a float.")
            filters.pop('weight_kg')
    return filters

@app.route('/people/find', methods=['GET'])
def find_people():
    filters = extract_filters(request.args)
    print(f"Filters received: {filters}")
    session = get_session()
    people = query_people_by_filters(session, filters)
    print(f"Found {len(people)} people matching filters.")
    schema = PeopleResponseSchema()
    response_data = {
        "success": True,
        "data": {
            "total": len(people),
            "results": [person.name for person in people]
        }
    }
    validated_data = schema.load(response_data)
    return jsonify(validated_data)

#Extra 1
#People who like both sushi and ramen
@app.route('/people/sushi_ramen', methods=['GET'])
def get_sushi_and_ramen():
    session = get_session()
    count = get_people_like_shushi_and_ramen(session)
    return jsonify({"success": True, "data": count})

#Extra 2
#People with average weight above 70 grouped by hair color
@app.route('/people/avg_weight_above_70_hair', methods=['GET'])
def get_avg_weight_above_70_hair():
    session = get_session()
    data = get_avg_weight_above_70_by_hair(session)
    return jsonify({"success": True, "data": data})

#Extra 3
#Most common food overall
@app.route('/people/most_common_food_overall', methods=['GET'])
def get_most_common_food_overall():
    session = get_session()
    data = get_most_common_food(session)
    return jsonify(data)

#Extra 4
#Average weight grouped by nationality and hair color
@app.route('/people/avg_weight_nationality_hair', methods=['GET'])
def get_avg_weight_nationality_hair():
    session = get_session()
    data = get_avg_weight_by_nationality_and_hair(session)
    return jsonify(data)

#Extra 5
#The top 2 oldest people per nationality
@app.route('/people/top_oldest_nationality', methods=['GET'])
def  top_oldest_nationality():
    session = get_session()
    data = get_top_oldest_natuinality(session)
    return jsonify(data)

#Extra 6
#People ranked by how many hobbies they have (Top 3)
@app.route('/people/top_hobbies', methods=['GET'])
def get_top_hobbies():
    session = get_session()
    data = top_hobbies(session)
    return jsonify(data)

#Extra 7
#Average height by nationality and average in general
@app.route("/people/avg_height_nationality_general")
def get_avg_height_nationality_general():
    session = get_session()
    data = avg_height_nationality_general(session)
    return jsonify(data)

if __name__ == '__main__':
    session = get_session()
    app.run(host='0.0.0.0', port=4000)
