from flask import Flask, jsonify, request
from . import services

def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    if testing:
        app.config["TESTING"] = True
        app.config["PROPAGATE_EXCEPTIONS"] = False

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.post("/monster")
    def monster():
        try:
            payload = request.get_json(silent=True) or {}
            idx = payload.get("monster_index", "")
            services.validate_monster_index(idx)
            data = services.fetch_monster(idx)
            return jsonify(data), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    return app

app = create_app()