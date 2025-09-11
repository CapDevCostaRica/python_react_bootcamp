
from flask import Flask, request, jsonify, abort
from app.telemetry import logger
from app.api.personAPI import (
    getPersons,
    getSushiAndRamenCountReport,
    getMostCommonFoodReport,
    getAvgWeightAbove70HairReport,
    getAverageWeightByNationalityAndHairReport,
    getTopOldestByNationalityReport,
    getTopPeopleByHobbiesCountReport,
    getAverageHeightByNationalityAndGeneralReport
)

app = Flask(__name__)

@app.route('/')
def health():
    return {'status': 'ok'}


# GET /people/find endpoint with filters[<field>]=value
@app.route('/people/find', methods=['GET'])
def findPeople():
    logger.info(f"Received request from {request.remote_addr}")
    try:
        data = getPersons(request)
        logger.info(f"Sending response to {request.remote_addr}")
        return jsonify({
            "success": True,
            "data": {
                "total": len(data),
                "results": data
            }
        })
    except ValueError as e:
        logger.error(f"Bad request: {e}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Internal error: {e}")
        abort(500, description="Internal Server Error")

@app.route('/people/sushi_ramen', methods=['GET'])
def reportSushiRamen():
    logger.info(f"Received request from {request.remote_addr}")
    try:
        data = getSushiAndRamenCountReport()
        logger.info(f"Sending response to {request.remote_addr}")
        return jsonify({
            "success": True,
            "data": data
        })
    except ValueError as e:
        logger.error(f"Bad request: {e}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Internal error: {e}")
        abort(500, description="Internal Server Error")

@app.route('/people/avg_weight_above_70_hair', methods=['GET'])
def avgWeightAbove70Hair():
    logger.info(f"Received request from {request.remote_addr}")
    try:
        data = getAvgWeightAbove70HairReport()
        logger.info(f"Sending response to {request.remote_addr}")
        return jsonify({
            "success": True,
            "data": data
        })
    except ValueError as e:
        logger.error(f"Bad request: {e}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Internal error: {e}")
        abort(500, description="Internal Server Error")

@app.route('/people/most_common_food_overall', methods=['GET'])
def reportMostCommonFood():
    logger.info(f"Received request from {request.remote_addr}")
    try:
        data = getMostCommonFoodReport()
        logger.info(f"Sending response to {request.remote_addr}")
        return jsonify({
            "success": True,
            "data": data
        })
    except ValueError as e:
        logger.error(f"Bad request: {e}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Internal error: {e}")
        abort(500, description="Internal Server Error")

@app.route('/people/avg_weight_nationality_hair', methods=['GET'])
def reportAvgWeightNationalityHair():
    logger.info(f"Received request from {request.remote_addr}")
    try:
        data = getAverageWeightByNationalityAndHairReport()
        logger.info(f"Sending response to {request.remote_addr}")
        return jsonify({
            "success": True,
            "data": data
        })
    except ValueError as e:
        logger.error(f"Bad request: {e}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Internal error: {e}")
        abort(500, description="Internal Server Error")

@app.route('/people/top_oldest_nationality', methods=['GET'])
def reportTopOldestNationality():
    logger.info(f"Received request from {request.remote_addr}")
    try:
        data = getTopOldestByNationalityReport()
        logger.info(f"Sending response to {request.remote_addr}")
        return jsonify({
            "success": True,
            "data": data
        })
    except ValueError as e:
        logger.error(f"Bad request: {e}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Internal error: {e}")
        abort(500, description="Internal Server Error")

@app.route('/people/top_hobbies', methods=['GET'])
def reportTopHobbies():
    logger.info(f"Received request from {request.remote_addr}")
    try:
        data = getTopPeopleByHobbiesCountReport()
        logger.info(f"Sending response to {request.remote_addr}")
        return jsonify({
            "success": True,
            "data": data
        })
    except ValueError as e:
        logger.error(f"Bad request: {e}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Internal error: {e}")
        abort(500, description="Internal Server Error")

@app.route('/people/avg_height_nationality_general', methods=['GET'])
def reportAvgHeightNationalityGeneral():
    logger.info(f"Received request from {request.remote_addr}")
    try:
        data = getAverageHeightByNationalityAndGeneralReport()
        logger.info(f"Sending response to {request.remote_addr}")
        return jsonify({
            "success": True,
            "data": data
        })
    except ValueError as e:
        logger.error(f"Bad request: {e}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Internal error: {e}")
        abort(500, description="Internal Server Error")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
