
from flask import Flask, request, jsonify, abort
from app.telemetry import logger
from app.api.personAPI import getPersons


app = Flask(__name__)

@app.route('/')
def health():
    return {'status': 'ok'}


# GET /people/find endpoint with filters[<field>]=value
@app.route('/people/find', methods=['GET'])
def find_people():
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
