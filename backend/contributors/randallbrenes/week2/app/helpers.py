from flask import jsonify
from marshmallow import ValidationError

def parse_response(response_obj):
    code = response_obj.get('code', 500)
    del response_obj['code']

    return jsonify(response_obj), code

def field_value(value: str):
    if value.isdigit():
        return int(value)
    try:
        return float(value)
    except ValueError:
        pass
    if value.lower() in ["true", "false"]:
        return value.lower() == "true"
    return value

def parse_query_string(args):
    result = { "filters": {} }
    for key, value in args.items():
        # 8:-1 remove filters[] string
        field_name = key[8:-1].replace('"', "").replace("'", "")
        result["filters"][field_name] = field_value(value)
    return result

def execute_service(service_method, input_data=None, response_schema=None, input_schema=None):
    if not input_schema is None:
        try:
            input_data = input_schema.load(input_data)
        except ValidationError as err:
            return jsonify({"success": False, "message": err.messages, "code": 400}), 400
    try:
        if input_data is not None:
            response = service_method(input_data)
        else:
            response = service_method()

        if response_schema:
            response_schema.load(response)

    except ValidationError as err:
        response = {"success": False, "message": err.messages, "code": 400}
    except Exception as e:
        response = {"success": False, "message": str(e), "code": 500}

    return parse_response(response)
