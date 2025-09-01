from http import HTTPStatus

from authentication import JWTError, decode_jwt
from response import make_response
from schemas import ErrorSchema


def require_role(*expected_roles: list[str]):
    def decorator(func):
        def wrapper(event, context, *args, **kwargs):
            headers = event.get("headers") or {}
            auth = headers.get("Authorization") or ""

            if not auth.startswith("Bearer "):
                return make_response(
                    HTTPStatus.UNAUTHORIZED,
                    ErrorSchema(error="Unauthorized"),
                )

            try:
                claims = decode_jwt(auth.split(" ", 1)[1].strip())

            except JWTError as e:
                return make_response(
                    HTTPStatus.UNAUTHORIZED,
                    ErrorSchema(error=str(e)),
                )

            if claims.get("role") not in expected_roles:
                return make_response(
                    HTTPStatus.FORBIDDEN,
                    ErrorSchema(error="Forbidden"),
                )

            return func(event, context, *args, **kwargs)

        return wrapper

    return decorator
