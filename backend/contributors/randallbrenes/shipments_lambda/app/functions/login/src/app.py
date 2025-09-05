import base64
import json
from http import HTTPStatus

from app.common.python.common.database.models import User
from app.common.python.common.database.database import get_session
from app.common.python.common.response.response import send_response
from app.common.python.common.schema.login import LoginSchema
from app.common.python.common.auth.auth import encode_jwt

def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def handler(event, context):
    try:
        body = event.get("body", {})

        if event.get("isBase64Encoded"):
            body = base64.b64decode(body)
        
        json_body = json.loads(body)
    except Exception as e:
        return send_response({ "error": str(e) }, HTTPStatus.BAD_REQUEST)

    try:
        body_data = LoginSchema().load(json_body)

        with get_session() as db:
            user = db.query(User).filter(User.username == body_data.get("username")).first()
            if not user:
                return send_response({ "error": "Invalid user" }, HTTPStatus.NOT_FOUND)
            
            token = encode_jwt(to_dict(user))
        
        return send_response({"access_token": token, "token_type": "Bearer"}, HTTPStatus.OK)

    except Exception as e:
            return send_response({ "error": str(e) }, HTTPStatus.BAD_REQUEST)