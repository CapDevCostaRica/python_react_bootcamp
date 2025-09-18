import os
import sys
import pytest

sys.path.append('/app/framework')
sys.path.append('/app/examples')
from test_examples import Monster, Base

from contributors.Luch1f3rchoCR.ex04_testing.app.main import create_app

_shared_session = None

def get_db_session():
    global _shared_session
    return _shared_session

@pytest.fixture
def app():
    app = create_app(testing=True)
    return app

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
        idx = index or f"test-monster-{uuid.uuid4().hex[:8]}"
        nm = name or f"Test Monster {idx}"
        data = {
            "index": idx,
            "name": nm,
            "type": "beast",
            "size": "Medium",
            "alignment": "neutral",
            "armor_class": 12,
            "hit_points": 20,
            "challenge_rating": 1,
            "url": f"/api/monsters/{idx}"
        }
        data.update(kwargs)
        return data
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
    import requests
    from unittest.mock import Mock
    mock_response = Mock()
    mock_response.json.return_value = external_api_monster_response
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200
    monkeypatch.setattr(requests, "get", lambda *a, **k: mock_response)
    return mock_response

@pytest.fixture
def mock_external_api_failure(monkeypatch):
    import requests
    def _fail(*a, **k):
        raise requests.ConnectionError("External API is down")
    monkeypatch.setattr("requests.get", _fail)

@pytest.fixture
def mock_external_api_timeout(monkeypatch):
    import requests
    def _timeout(*a, **k):
        raise requests.Timeout("Request timed out")
    monkeypatch.setattr("requests.get", _timeout)

@pytest.fixture
def mock_external_api_404(monkeypatch):
    import requests
    from unittest.mock import Mock
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    monkeypatch.setattr("requests.get", lambda *a, **k: mock_response)

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "testing")
    monkeypatch.setenv("EXTERNAL_API_TIMEOUT", "1")
    monkeypatch.setenv("CACHE_TTL", "300")
    yield