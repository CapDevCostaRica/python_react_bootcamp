from http import HTTPStatus
from app.common.python.common.response import make_response
from app.common.python.common.authentication.jwt import decode_jwt, JWTError

import logging

logger = logging.getLogger()

def require_role(*expected_roles: list[str]):
    def decorator(func):
        def wrapper(event, context, *args, **kwargs):
            headers = event.get("headers") or {}
            auth_header = headers.get("Authorization","")
            if not auth_header.startswith("Bearer "):
                return make_response(
                    {"error": "Unauthorized"},
                    HTTPStatus.UNAUTHORIZED
                )
            
            try:
                claims = decode_jwt(auth_header.split(" ",1)[1].strip())

            except JWTError as e:
                logger.error(f"JWT Error: {str(e)}")
                return make_response(
                    {"error": "Unauthorized"},
                    HTTPStatus.UNAUTHORIZED
                )
            
            if claims.get("role") not in expected_roles:
                return make_response(
                    {"error": "Forbidden"},
                    HTTPStatus.FORBIDDEN
                )
            
            event["claims"] = claims
 
            return func(event, context, *args, **kwargs)
        
        return wrapper
    
    return decorator