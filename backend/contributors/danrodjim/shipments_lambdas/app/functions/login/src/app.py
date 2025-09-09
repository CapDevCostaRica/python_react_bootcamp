from app.common.python.common.authentication.jwt import encode_jwt
from app.common.python.common.database.models import User
from app.common.python.common.database.database import get_session
from app.common.python.common.response.make_response import make_response
from .schema import LoginRequestSchema
from http import HTTPStatus
import base64
import json

def handler(event, context):
    try:
        body = event.get("body") or {}

        if event.get("isBase64Enconded"):
            body = base64.b64decode(body).decode()

        json_body = json.loads(body)

    except:
        return make_response(
            {"error": "Invalid JSON body"},
            HTTPStatus.BAD_REQUEST
        )
    
    body = LoginRequestSchema().load(json_body)
    username = body.get("username")

    with get_session() as session:
        user = session.query(User).filter(User.username==username).first()

        if not user:
            return make_response(
                {"error": "Invalid credentials"},
                HTTPStatus.NOT_FOUND
            )
        
        payload = {
            "id": user.id,
            "role": user.role
        }
        
        token = encode_jwt(payload)

        return make_response(
            {"access_token": token, "token_type": "Bearer"},
            HTTPStatus.OK
        )
