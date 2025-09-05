from http import HTTPStatus

def send_response(data, status = HTTPStatus.OK):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": data
    }