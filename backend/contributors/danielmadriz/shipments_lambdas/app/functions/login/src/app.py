from app.common.python.common.authentication import encode_jwt
from app.common.python.common.database.database import get_session
from app.common.python.common.database import models
from app.common.python.common.response import make_response
from http import HTTPStatus
from .schema import LoginRequestSchema

import base64
import json

def handler(event, context):
    try:
        body = event.get("body") or ()

        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode()
        
        json_body = json.loads(body)

    except:
        return make_response(
            {"error": "Invalid JSON body"},
            HTTPStatus.BAD_REQUEST
            )

    body  = LoginRequestSchema().load(json_body)
    username = body.get("username")

    with get_session() as session:
        user = session.query(models.User).filter(models.User.username == username).first()

        if not user:
            return make_response(
                {"error": "Invalid Credentials"},
                HTTPStatus.NOT_FOUND
            )

        token = encode_jwt(user._asdict())

        return make_response(
            {"access_token": token, "token_type": "bearer"},
            HTTPStatus.OK
        )


    