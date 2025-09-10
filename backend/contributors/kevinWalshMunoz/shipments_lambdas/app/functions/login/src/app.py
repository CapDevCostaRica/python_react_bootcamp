from app.common.python.common.authentication.jwt import encode_jwt
from app.common.python.common.database import models

from app.common.python.common.response.make_response import make_response
from app.common.python.common.database.database import get_session
from .schema import LoginRequestSchema


import json
import base64
from http import HTTPStatus

def handler(event, context):
	try:
		body = event.get("body") or "{}"

		if event.get("isBase64Encoded"):
			body = base64.b64decode(body).decode()

		json_body = json.loads(body)
		username = json_body.get("username")
	except:
		return make_response(
			{"error": "Invalid request body"},
			HTTPStatus.BadRequest,
		)
	
	body = LoginRequestSchema().load(json_body)
	username = body.get("username")

	with get_session() as session:
		user = session.query(models.User).filter(models.User.username == username).first()

		if not user:
			return make_response(
				{"error": "Invalid credentials"},
				HTTPStatus.NOT_FOUND,
			)

		payload = {
			"userId": user.id,
			"role": user.role,
		}

		token = encode_jwt(payload)
		
		return make_response(
			{"access_token": token, "token_type": "bearer"},
			HTTPStatus.OK
		)
