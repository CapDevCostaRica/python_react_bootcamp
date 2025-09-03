from flask import Flask
from .blueprints import people_bp

app = Flask(__name__)
app.register_blueprint(people_bp)

@app.get("/")
def health():
    return {"status": "ok"}