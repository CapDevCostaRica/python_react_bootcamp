from flask import Flask, jsonify, request, abort
from services.telemetry import setupLogger
from api.monsters.api import getMonster, listMonsters

app = Flask(__name__)
app.config['DND_API_BASE_URL'] = 'https://www.dnd5eapi.co'
logger = setupLogger()

@app.route('/get', methods=['POST'])
def get():
    logger.info(f"Received request from {request.remote_addr}")
    try:
        data, code = getMonster(request)
        if code == 404:
            logger.info(f"Monster not found")
            abort(404, description="Monster not found")
        logger.info(f"Sending response to {request.remote_addr}")
        return jsonify(data)
    except ValueError as e:
        logger.error(f"Bad request: {e}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Internal error: {e}")
        abort(500, description="Internal Server Error")

@app.route('/list', methods=['POST'])
def list():
    logger.info(f"Received request from {request.remote_addr}")
    try:
        data = listMonsters(request)
        logger.info(f"Sending response to {request.remote_addr}")
        return jsonify(data)
    except ValueError as e:
        logger.error(f"Bad request: {e}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Internal error: {e}")
        abort(500, description="Internal Server Error")

@app.route('/health')
def health():
    logger.info(f"Received request from {request.remote_addr}")
    logger.info(f"Sending response to {request.remote_addr}")
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)