from backend.contributors.crisarias.shipments_lambdas.app.common.python.shared.security.jwt import encode_jwt
from app.common.python.shared.infrastructure.database import get_db_session
from app.common.python.shared.infrastructure.telemetry import logger
from app.common.python.shared.domain.models import User
from app.common.python.shared.infrastructure.response import make_response
from schema import LoginRequestSchema


import base64
import json
from http import HTTPStatus
from marshmallow import ValidationError

def handler(event, context):
    # Extract username and password from the event
    try:
        body = event.get("body", {})

        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode("utf-8")

        body = json.loads(body)
    except:
        logger.error("Failed to parse request body")
        return make_response({"error": "Invalid request body"}, HTTPStatus.BAD_REQUEST)
    
    try:
        body = LoginRequestSchema.load(body)
        username = body["username"]
    except ValidationError as e:
        logger.error(f"Validation error: {e.messages}")
        return make_response({"error": str(e)}, HTTPStatus.BAD_REQUEST)
    
    with get_db_session() as session:
        user = session.query(User).filter(User.username == username).first()

        if not user:
            logger.warning(f"User '{username}' not found")
            return make_response({"error": "Invalid username"}, HTTPStatus.NOT_FOUND)

        # Generate JWT token
        token = encode_jwt(user._asdict())

        return make_response({
            "token": token,
            "token_type": "Bearer"
        }, HTTPStatus.OK)
