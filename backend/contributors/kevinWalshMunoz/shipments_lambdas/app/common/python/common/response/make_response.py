from http import HTTPStatus

def make_response(data, status_code=HTTPStatus.OK):
	return {
		"statusCode": status_code.value,
		"headers": {
      "Content-Type": "application/json"
    },
		"body": data
	}