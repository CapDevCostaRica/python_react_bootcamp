from http import HTTPStatus

def make_response(data, status_code: HTTPStatus=HTTPStatus.OK) -> dict:
    return {
        "statusCode": status_code,        
        "headers": {
            "Content-Type": "application/json"
        },
        "body": data,
    }