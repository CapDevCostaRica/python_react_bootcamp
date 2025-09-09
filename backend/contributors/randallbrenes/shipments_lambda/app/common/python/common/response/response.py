from http import HTTPStatus
import json

def send_response(data, status = HTTPStatus.OK):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": data
    }