import os, json
from flask import Flask, jsonify, request, Blueprint
from sqlalchemy import select
from .database import SessionLocal
from .models import User, Shipment
from .auth import make_token, decode_token
from .seeds import run as seed_run

bp = Blueprint("ex03", __name__)

def get_db():
    return SessionLocal()

def require_auth(req):
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise PermissionError("Missing or invalid Authorization header")
    token = auth.split(" ", 1)[1].strip()
    return decode_token(token)

def can_view(payload, s: Shipment):
    role = payload.get("role")
    if role == "global_manager":
        return True
    if role in ("store_manager", "warehouse_staff"):
        store_id = payload.get("store_id")
        return s.origin_store == store_id or s.destination_store == store_id
    if role == "carrier":
        return s.carrier_id and s.carrier_id == payload.get("carrier_id")
    return False

def allowed_transition(role, current, target):
    if role == "warehouse_staff":
        return (current, target) in {("created","in_transit"), ("in_transit","delivered")}
    return False

@bp.get("/health")
def health():
    return jsonify({"ok": True})

@bp.post("/login")
def login():
    data = request.get_json(force=True) or {}
    username, password = data.get("username"), data.get("password")
    db = get_db()
    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if not user or user.password != password:
        return jsonify({"error": "invalid_credentials"}), 401
    token = make_token(user.id, user.role, user.store_id, user.carrier_id)
    return jsonify({"token": token, "user": {
        "id": user.id, "role": user.role, "store_id": user.store_id, "carrier_id": user.carrier_id
    }}), 200

@bp.post("/shipment/list")
def list_shipments():
    payload = require_auth(request)
    db = get_db()
    filters = request.get_json(force=True) or {}
    q = select(Shipment)
    if "status" in filters:  q = q.where(Shipment.status == filters["status"])
    if "carrier" in filters: q = q.where(Shipment.carrier_id == filters["carrier"])
    if "id" in filters:      q = q.where(Shipment.id == filters["id"])
    results = db.execute(q).scalars().all()
    visible = [s for s in results if can_view(payload, s)]
    return jsonify([{
        "id": s.id, "origin_store": s.origin_store, "destination_store": s.destination_store,
        "carrier_id": s.carrier_id, "status": s.status, "location": s.location
    } for s in visible]), 200

@bp.post("/shipment")
def create_shipment():
    payload = require_auth(request)
    if payload.get("role") != "warehouse_staff":
        return jsonify({"error": "forbidden"}), 403
    data = request.get_json(force=True) or {}
    for k in ("origin_store","destination_store","carrier_id"):
        if not data.get(k):
            return jsonify({"error": "missing_fields",
                            "required": ["origin_store","destination_store","carrier_id"]}), 400
    db = get_db()
    s = Shipment(
        origin_store=data["origin_store"],
        destination_store=data["destination_store"],
        carrier_id=data["carrier_id"],
        status="created",
        location=data.get("location")
    )
    db.add(s); db.commit(); db.refresh(s)
    return jsonify({"id": s.id, "status": s.status}), 201

@bp.post("/shipment/<int:shipment_id>")
def update_shipment(shipment_id: int):
    payload = require_auth(request)
    role = payload.get("role")
    db = get_db()
    s = db.get(Shipment, shipment_id)
    if not s:
        return jsonify({"error": "not_found"}), 404
    if not can_view(payload, s):
        return jsonify({"error": "forbidden"}), 403

    data = request.get_json(force=True) or {}
    new_status = data.get("status")
    new_location = data.get("location")

    if role == "carrier":
        if new_status and new_status != s.status:
            return jsonify({"error": "carrier_cannot_change_status"}), 403
        if s.status != "in_transit":
            return jsonify({"error": "carrier_location_only_in_transit"}), 403
        if not new_location:
            return jsonify({"error": "no_location_provided"}), 400
        s.location = new_location
        db.commit(); db.refresh(s)
        return jsonify({"ok": True, "id": s.id, "status": s.status, "location": s.location}), 200

    if role == "warehouse_staff" and new_status:
        if not allowed_transition(role, s.status, new_status):
            return jsonify({"error": "invalid_transition"}), 400
        s.status = new_status
        if new_location: s.location = new_location
        db.commit(); db.refresh(s)
        return jsonify({"ok": True, "id": s.id, "status": s.status, "location": s.location}), 200

    return jsonify({"error": "no_update_permission"}), 403

def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app

app = create_app()

if os.environ.get("RUN_SEEDS_ON_BOOT", "1") == "1":
    try:
        seed_run()
    except Exception:
        pass

def handler(event, context):
    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        import base64; body = base64.b64decode(body).decode("utf-8")
    try:
        data = json.loads(body) if body else {}
    except Exception:
        data = {}
    headers = event.get("headers") or {}
    method = event.get("requestContext", {}).get("http", {}).get("method", "POST")
    path = event.get("rawPath", "")

    with app.test_request_context(path=path, method=method, headers=headers, json=data):
        if path == "/login" and method == "POST": resp = login()
        elif path == "/shipment/list" and method == "POST": resp = list_shipments()
        elif path == "/shipment" and method == "POST": resp = create_shipment()
        elif path.startswith("/shipment/") and method == "POST":
            try: sid = int(path.rsplit("/", 1)[1])
            except Exception:
                return {"statusCode": 400, "headers": {"Content-Type":"application/json"},
                        "body": json.dumps({"error":"bad_path"})}
            resp = update_shipment.__wrapped__(sid)
        else:
            return {"statusCode": 404, "headers": {"Content-Type":"application/json"},
                    "body": json.dumps({"error":"not_found"})}

        data_out, status = resp
        return {"statusCode": status, "headers": {"Content-Type":"application/json"},
                "body": json.dumps(data_out)}