from http import HTTPStatus

from marshmallow import Schema


def make_response(status_code: HTTPStatus, data: Schema):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": data.dump(),
    }
