from infrastructure.response import make_response
from infrastructure.telemetry import logger
from jwt import decode_jwt, JWTError

from http import HTTPStatus

def require_role(*expected_roles: list[str]):
    def decorator(func):
        def wrapper(event, context, *args, **kwargs):
            headers = event.get("headers", {})
            auth_header = headers.get("Authorization", "")

            if not auth_header.startswith("Bearer "):
                logger.warning("Missing or invalid Authorization header.")
                return make_response({
                    "error": "Unauthorized: Missing or invalid Authorization header."
                }, HTTPStatus.UNAUTHORIZED)
            
            try:
                token = auth_header.split(" ",1)[1].strip()
                claims = decode_jwt(token)

            except (IndexError, JWTError):
                logger.warning("Invalid or missing JWT token.")
                return make_response({
                    "error": "Unauthorized: Invalid token."
                }, HTTPStatus.UNAUTHORIZED)

            if not claims.get("role") in expected_roles:
                logger.warning(f"User role '{claims.get('role')}' is not authorized.")
                return make_response({
                    "error": "Forbidden: You do not have the required role."
                }, HTTPStatus.FORBIDDEN)

            return func(event, context, *args, **kwargs)
        return wrapper
    return decorator