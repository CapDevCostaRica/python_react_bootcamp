from http import HTTPStatus

from flask import Flask, jsonify, request


def no_function_defined(*args, **kwargs):
    return {
        "statusCode": HTTPStatus.NOT_FOUND,
        "body": {},
    }


try:
    from app.functions.shipment_list.src.app import handler as list_shipments_handler

except ImportError:
    list_shipments_handler = no_function_defined
try:
    from app.functions.login.src.app import handler as login_handler

except ImportError:
    login_handler = no_function_defined


try:
    from app.functions.create_shipment.src.app import handler as create_shipment

except ImportError:
    create_shipment = no_function_defined

try:
    from app.functions.update_shipment.src.app import handler as update_shipment

except ImportError:
    update_shipment = no_function_defined

app = Flask(__name__)


@app.route("/")
def health():
    return {"status": "ok"}


@app.post("/login", endpoint="login")
def login_handler_route():
    event = {
        "headers": dict(request.headers),
        "body": request.get_data(as_text=True) or "",
        "pathParameters": {},
    }
    context = {
        "agent": "Internal Lambda Executor 1.0",
    }

    response = login_handler(
        event=event,
        context=context,
    )
    return jsonify(response.get("body")), response.get("statusCode", 200)

@app.post("/shipment/list", endpoint="shipments_list")
@app.post("/shipment/<int:shipment_id>", endpoint="shipment")
@app.post("/shipment/", endpoint="shipments")
def shipments_handler(shipment_id: str | None = None):
    endpoint = request.endpoint
    print(f"DEBUG: endpoint = {endpoint}, shipment_id = {shipment_id}")
    handlers = {
        "shipments_list": list_shipments_handler,
        "shipments": create_shipment,
        "shipment": update_shipment,
    }

    if not endpoint or not (handler := handlers.get(endpoint)):
        print(f"DEBUG: Using no_function_defined for endpoint: {endpoint}")
        handler = no_function_defined

    event = {
        "headers": dict(request.headers),
        "body": request.get_data(as_text=True) or "",
        "pathParameters": {"shipment_id": shipment_id} if shipment_id else {},
    }
    context = {
        "agent": "Internal Lambda Executor 1.0",
    }

    response = handler(
        event=event,
        context=context,
    )
    return jsonify(response.get("body")), response.get("statusCode", 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
