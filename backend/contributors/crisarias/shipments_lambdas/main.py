from http import HTTPStatus
from app.common.python.shared.infrastructure.telemetry import logger
from flask import Flask, jsonify, request


def no_function_defined(*args, **kwargs):
    return {
        "statusCode": HTTPStatus.NOT_FOUND,
        "body": {},
    }


try:
    from app.functions.list_shipments.src.app import handler as list_shipments_handler
except ImportError as e:
    logger.error(f"Failed to import list shipments handler: {e}")
    list_shipments_handler = no_function_defined

try:
    from app.functions.login.src.app import handler as login_handler
except ImportError as e:
    logger.error(f"Failed to import login handler: {e}")
    login_handler = no_function_defined


try:
    from app.functions.create_shipment.src.app import handler as create_shipment
except ImportError as e:
    logger.error(f"Failed to import create shipment handler: {e}")
    create_shipment = no_function_defined

try:
    from app.functions.update_shipment.src.app import handler as update_shipment
except ImportError as e:
    logger.error(f"Failed to import update shipment handler: {e}")
    update_shipment = no_function_defined

app = Flask(__name__)


@app.route("/")
def health():
    return {"status": "ok"}


@app.post("/login", endpoint="login")
@app.post("/shipment/list", endpoint="shipments_list")
@app.post("/shipment/", endpoint="shipments")
@app.post("/shipment/<int:shipment_id>", endpoint="shipment")
def shipments_handler(shipment_id: str | None = None):
    endpoint = request.endpoint
    logger.info(f"Received {endpoint} request from {request.remote_addr}")
    logger.info(f"Shipment list handler: {list_shipments_handler.__name__}")
    handlers = {
        "login": login_handler,
        "shipments_list": list_shipments_handler,
        "shipments": create_shipment,
        "shipment": update_shipment,
    }


    logger.info(f"Handling {endpoint} request")
    logger.debug(f"Request headers: {dict(request.headers)}")
    logger.debug(f"Request body: {request.get_data(as_text=True)}")

    if not endpoint or not (handler := handlers.get(endpoint)):        
        handler = no_function_defined

    event = {
        "headers": dict(request.headers),
        "body": request.get_data(as_text=True) or "",
        "pathParameters": {"shipment_id": shipment_id} if shipment_id else {},
    }
    context = {
        "agent": "Internal Lambda Executor 1.0",
    }

    logger.info(f"Invoking handler for handler {handler.__name__}")

    response = handler(
        event=event,
        context=context,
    )
    return jsonify(response.get("body")), response.get("statusCode", 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
