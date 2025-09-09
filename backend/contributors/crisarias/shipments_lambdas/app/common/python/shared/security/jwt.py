import base64
import hashlib
import hmac
import json
import os
import time

SECRET_KEY = os.getenv("SECRET_KEY", "not-secret-at-all")
TTL = int(os.getenv("TOKEN_TTL_SECONDS", 900))  # Default to 15 minutes


def _b64_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _b64_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)

    return base64.urlsafe_b64decode(s + pad)


def _sign(data: str, secret: str) -> str:
    return _b64_encode(
        hmac.new(secret.encode(), data.encode(), hashlib.sha256).digest()
    )


class JWTError(Exception): ...


def encode_jwt(payload: dict, secret: str = SECRET_KEY) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        **payload,
        "iat": payload.get("iat", now),
        "exp": payload.get("exp", now + TTL),
    }
    header_b64 = _b64_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64_encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = _sign(f"{header_b64}.{payload_b64}", secret)

    return f"{header_b64}.{payload_b64}.{signature}"


def decode_jwt(token: str, secret: str = SECRET_KEY) -> dict:
    try:
        header_b64, payload_b64, signature = token.split(".")

    except ValueError:
        raise JWTError("Invalid token format")

    header = json.loads(_b64_decode(header_b64))

    if header.get("alg") != "HS256":
        raise JWTError("Unsupported algorithm")

    if not hmac.compare_digest(signature, _sign(f"{header_b64}.{payload_b64}", secret)):
        raise JWTError("Invalid signature")

    claims = json.loads(_b64_decode(payload_b64))

    if int(time.time()) > claims.get("exp", 0):
        raise JWTError("Token has expired")

    return claims
