import sys
import time
import warnings
import pytest
from unittest.mock import Mock

sys.path.append('/app/examples')
from test_examples import Monster, Base

_shared_session = None

def get_db_session():
    global _shared_session
    return _shared_session

@pytest.fixture
def app():
    from flask import Flask, request, jsonify
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })

    @app.route('/monsters', methods=['POST'])
    def monsters_list():
        try:
            data = request.get_json()
            if not data or "resource" not in data:
                return jsonify({"error": "Missing resource field"}), 400
            if data["resource"] != "monsters":
                return jsonify({"error": "Invalid resource"}), 400
            session = get_db_session()
            if session:
                monsters = session.query(Monster).all()
                return jsonify({
                    "count": len(monsters),
                    "results": [
                        {"index": m.index, "name": m.name, "url": f"/api/monsters/{m.index}"}
                        for m in monsters
                    ]
                })
            return jsonify({
                "count": 2,
                "results": [
                    {"index": "dragon", "name": "Dragon", "url": "/api/monsters/dragon"},
                    {"index": "orc", "name": "Orc", "url": "/api/monsters/orc"}
                ]
            })
        except Exception:
            return jsonify({"error": "Invalid JSON"}), 400

    @app.route('/monster', methods=['POST'])
    def monster_get():
        try:
            data = request.get_json()
            if not data or "monster_index" not in data:
                return jsonify({"error": "Missing monster_index field"}), 400
            monster_index = data["monster_index"]
            session = get_db_session()
            if session:
                monster = session.query(Monster).filter_by(index=monster_index).first()
                if monster:
                    result = {"index": monster.index, "name": monster.name, **(monster.data or {})}
                    return jsonify(result)
            return jsonify({
                "index": monster_index,
                "name": f"Test {monster_index.title()}",
                "type": "humanoid",
                "challenge_rating": 1,
                "hit_points": 15,
                "armor_class": 13
            })
        except Exception:
            return jsonify({"error": "Invalid JSON"}), 400

    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session():
    global _shared_session
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        'sqlite:///:memory:',
        echo=False,
        poolclass=StaticPool,
        connect_args={'check_same_thread': False}
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    _shared_session = session
    yield session
    session.rollback()
    session.close()
    _shared_session = None

@pytest.fixture
def clean_db(db_session):
    db_session.commit()
    yield db_session

@pytest.fixture
def sample_monster_data():
    return {
        "index": "ancient-red-dragon",
        "name": "Ancient Red Dragon",
        "size": "Gargantuan",
        "type": "dragon",
        "subtype": "",
        "alignment": "chaotic evil",
        "armor_class": 22,
        "hit_points": 546,
        "challenge_rating": 24,
        "url": "/api/monsters/ancient-red-dragon"
    }

@pytest.fixture
def monster_factory():
    def _create_monster(index=None, name=None, **kwargs):
        import uuid
        default_index = index or f"test-monster-{uuid.uuid4().hex[:8]}"
        default_name = name or f"Test Monster {default_index}"
        defaults = {
            "index": default_index,
            "name": default_name,
            "type": "beast",
            "size": "Medium",
            "alignment": "neutral",
            "armor_class": 12,
            "hit_points": 20,
            "challenge_rating": 1,
            "url": f"/api/monsters/{default_index}"
        }
        defaults.update(kwargs)
        return defaults
    return _create_monster

@pytest.fixture
def external_api_monster_response():
    return {
        "index": "orc",
        "name": "Orc",
        "size": "Medium",
        "type": "humanoid",
        "subtype": "orc",
        "alignment": "chaotic evil",
        "armor_class": 13,
        "hit_points": 15,
        "challenge_rating": 0.5,
        "url": "/api/monsters/orc"
    }

@pytest.fixture
def mock_external_api_success(monkeypatch, external_api_monster_response):
    mock_response = Mock()
    mock_response.json.return_value = external_api_monster_response
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock_response)
    return mock_response

@pytest.fixture
def mock_external_api_failure(monkeypatch):
    import requests
    def mock_request_failure(*args, **kwargs):
        raise requests.ConnectionError("External API is down")
    monkeypatch.setattr("requests.get", mock_request_failure)

@pytest.fixture
def mock_external_api_timeout(monkeypatch):
    import requests
    def mock_request_timeout(*args, **kwargs):
        raise requests.Timeout("Request timed out")
    monkeypatch.setattr("requests.get", mock_request_timeout)

@pytest.fixture
def mock_external_api_404(monkeypatch):
    import requests
    mock_response = Mock()
    mock_response.status_code = 404
    def _raise():
        raise requests.HTTPError("404 Not Found")
    mock_response.raise_for_status.side_effect = _raise
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock_response)

@pytest.fixture
def performance_monitor():
    start = time.time()
    yield
    if time.time() - start > 1.0:
        warnings.warn("Slow test detected")

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "testing")
    monkeypatch.setenv("EXTERNAL_API_TIMEOUT", "1")
    monkeypatch.setenv("CACHE_TTL", "300")