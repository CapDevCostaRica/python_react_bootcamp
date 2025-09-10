from http import HTTPStatus
import logging

from app.common.python.common.response.make_response import make_response
from app.common.python.common.authentication.jwt import decode_jwt, JWTError

logger = logging.getLogger()

def require_role(*expected_role: list[str]):
    def decorator(func):
        def wrapper(event, context, *args, **kwargs):
            header = event.get("headers", {})
            auth_header = header.get("Authorization")

            if not auth_header:
                return make_response(
                    {"error": "Authorization header missing"},
                    HTTPStatus.UNAUTHORIZED,
                )
            
            try:
                claims = decode_jwt(auth_header.split(" ", 1)[1].strip())

            except JWTError as e:
                logger.warning(f"JWT decoding error: {e}")
                return make_response(
                    {"error": "Invalid token"},
                    HTTPStatus.UNAUTHORIZED,
                )
            
            if claims.get("role") not in expected_role:
                return make_response(
                    {"error": "Forbidden"},
                    HTTPStatus.FORBIDDEN,
                )
            
            return func(event, context, *args, **kwargs)
        
        return wrapper
    
    return decorator