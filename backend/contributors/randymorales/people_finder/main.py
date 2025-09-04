from flask import Flask, request, jsonify
from app.services import (
    find_people_by_filters,
    get_sushi_ramen_lovers,
    get_avg_weight_above_70_by_hair,
    get_most_common_food,
    get_avg_weight_by_nationality_hair,
    get_top_oldest_by_nationality,
    get_top_people_by_hobbies,
    get_avg_height_by_nationality_and_general
)

app = Flask(__name__)

@app.route('/')
def health():
    return {'status': 'ok'}

@app.route('/people/find', methods=['GET'])
def find_people():
    """
    Find people based on multiple filter criteria
    Accepts filters as query parameters in format: filters[key]=value
    """
    try:
        # Get filters from query parameters
        filters = {}
        for key, value in request.args.items():
            if key.startswith('filters[') and key.endswith(']'):
                filter_key = key[8:-1]  # Remove 'filters[' and ']'
                # Convert age to int if it's a numeric value
                if filter_key == 'age' and value.isdigit():
                    filters[filter_key] = int(value)
                else:
                    filters[filter_key] = value

        # Use service to find people
        result_names, total = find_people_by_filters(filters)

        response = {
            "success": True,
            "data": {
                "total": total,
                "results": result_names
            }
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Extra Credit Endpoints

@app.route('/people/sushi_ramen', methods=['GET'])
def sushi_ramen_lovers():
    """Extra 1: People who like both sushi and ramen"""
    try:
        count = get_sushi_ramen_lovers()
        return jsonify({
            "success": True,
            "data": count
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/people/avg_weight_above_70_hair', methods=['GET'])
def avg_weight_above_70_hair():
    """Extra 2: People with average weight above 70 grouped by hair color"""
    try:
        data = get_avg_weight_above_70_by_hair()
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/people/most_common_food_overall', methods=['GET'])
def most_common_food_overall():
    """Extra 3: Most common food overall"""
    try:
        food = get_most_common_food()
        return jsonify({
            "success": True,
            "data": food
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/people/avg_weight_nationality_hair', methods=['GET'])
def avg_weight_nationality_hair():
    """Extra 4: Average weight grouped by nationality and hair color"""
    try:
        data = get_avg_weight_by_nationality_hair()
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/people/top_oldest_nationality', methods=['GET'])
def top_oldest_nationality():
    """Extra 5: The top 2 oldest people per nationality"""
    try:
        data = get_top_oldest_by_nationality()
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/people/top_hobbies', methods=['GET'])
def top_hobbies():
    """Extra 6: People ranked by how many hobbies they have (Top 3)"""
    try:
        data = get_top_people_by_hobbies()
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/people/avg_height_nationality_general', methods=['GET'])
def avg_height_nationality_general():
    """Extra 7: Average height by nationality and average in general"""
    try:
        data = get_avg_height_by_nationality_and_general()
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
