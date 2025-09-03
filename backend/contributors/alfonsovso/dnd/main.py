from flask import Flask
from .routes import bp as dnd_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(dnd_bp, url_prefix="/dnd")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
