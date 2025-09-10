from app.common.python.common.authentication.jwt import encode_jwt
from app.common.python.common.database import models

from app.common.python.common.response import make_response
from app.common.python.common.database import get_session
from .schema import LoginResponseSchema


import json
import base64
import http as HTTPStatus

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
	
	body = LoginResponseSchema().load(json_body)
	username = body.get("username")

	with get_session() as session:
		user = session.query(models.User).filter(models.User.username == username).first()

		if not user:
			return make_response(
				{"error": "Invalid credentials"},
				HTTPStatus.NotFound,
			)

		token = encode_jwt(user._asdict())
		
		return make_response(
			{"access_token": token, "token_type": "bearer"},
			HTTPStatus.OK
		)
