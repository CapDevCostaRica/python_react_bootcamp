import logging
import time
from http import HTTPStatus
from app.common.python.common.response.make_response import make_response
from app.common.python.common.authentication.jwt import decode_jwt, JWTError
from app.common.python.common.database.models import User
from app.common.python.common.database.database import get_session

logger = logging.getLogger()
now = int(time.time())

def require_role(*expected_roles: list[str]):
    def decorator(func):
        def wrapper(event, context, *args, **kwargs):
            headers = event.get("headers") or {}
            auth_header = headers.get("Authorization", "")

            if not auth_header.startswith("Bearer "):
                return make_response(
                    {"error": "Unauthorized"},
                    HTTPStatus.UNAUTHORIZED
                )
            
            try:
                claims = decode_jwt(auth_header.split(" ", 1)[1].strip())

            except JWTError as e:
                logger.warning("JWTError: %s", str(e))
                return make_response(
                    {"error": "Unauthorized"},
                    HTTPStatus.UNAUTHORIZED
                )
            
            if claims.get("role") not in expected_roles or claims.get("role") is None:
                return make_response(
                    {"error": "Forbidden"},
                    HTTPStatus.FORBIDDEN
                )
            
            identifier = claims.get("id")
            if identifier is None:
                return make_response(
                    {"error": "Forbidden"},
                    HTTPStatus.FORBIDDEN
                )
            else:
                with get_session() as session:
                    user = session.query(User).filter(User.id == identifier).first()

                if not user:
                    return make_response(
                        {"error": "Forbidden"},
                        HTTPStatus.FORBIDDEN
                    )
            
            exp = claims.get("exp")
            if exp is None:
                return make_response(
                    {"error": "Unauthorized"},
                    HTTPStatus.UNAUTHORIZED
                )
            elif now > exp:
                return make_response(
                    {"error": "Unauthorized"},
                    HTTPStatus.UNAUTHORIZED
                )
            
            event["claims"] = claims

            return func(event, context, *args, **kwargs)

        return wrapper
    
    return decorator