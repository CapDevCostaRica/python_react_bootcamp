import os, time, jwt

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALG = "HS256"
JWT_TTL = int(os.getenv("JWT_TTL_SECONDS", "3600"))

def make_token(user_id: int, role: str, store_id=None, carrier_id=None):
    exp = int(time.time()) + JWT_TTL
    payload = {"sub": str(user_id), "role": role, "exp": exp}
    if store_id:   payload["store_id"] = store_id
    if carrier_id: payload["carrier_id"] = carrier_id
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_token(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])