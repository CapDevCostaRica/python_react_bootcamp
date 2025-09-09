from http import HTTPStatus
from app.common.python.common.response.response import send_response
from app.common.python.common.auth.auth import decode_jwt, JWTError
import logging

logger = logging.getLogger()

def require_role(expected_roles: list[str]):
    def decorator(func):
        def wrapper(event, context, *args, **kwargs):
            headers = event.get("headers", {})
            auth_header = headers.get("Authorization", "")

            if not auth_header.startswith("Bearer "):
                return send_response({"error": "Unauthorized"}, HTTPStatus.UNAUTHORIZED)
            try:
                
                claims = decode_jwt(auth_header.split(" ", 1)[1].strip())

            except JWTError as e:
                logger.warning("JWT error: %s ", str(e))
                return send_response({"error": str(e)}, HTTPStatus.UNAUTHORIZED)

            if(claims.get("role") not in expected_roles):
                return send_response({"error": "Unauthorized"}, HTTPStatus.UNAUTHORIZED)

            event["user_data"] = claims
            return func(event, context, *args, **kwargs)

        return wrapper
    return decorator