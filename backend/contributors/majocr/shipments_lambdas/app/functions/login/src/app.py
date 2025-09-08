import base64
import json
from http import HTTPStatus

from app.common.python.common.authentication.jwt import encode_jwt
from app.common.python.common.database.models import User
from app.common.python.common.response.make_response import make_response
from app.common.python.common.database.database import get_session
from app.common.python.common.database import models
from app.common.python.common.authentication.jwt import encode_jwt
from app.schema import LoginRequestSchema


def handler(event, context):
    try:
        body = event.get("body") or {}
        
        if event.get("isBase64Encoded"):
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
        user = session.query(models.User).filter(models.User.username == username).first()
        
        if not user:
            return make_response(
                {"error": "Invalid credentials"},
                HTTPStatus.BAD_REQUEST
            )
        
        #token = encode_jwt(user._asdict())
        payload = {
            "sub": user.id,
            "role": user.role,
            "warehouse_id": user.warehouse_id,
            "iss": "shipments-api",
            "aud": "shipment-client",
        }
        token = encode_jwt(payload)
        
        return make_response(
            {"access_token": token, "token_type": "Bearer"},
            HTTPStatus.OK
        )
    