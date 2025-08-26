# conftest.py - Shared test fixtures for Testing Workshop
# Copy this file to your test directory and customize as needed

import pytest
import sys

# Add framework to Python path for workshop
sys.path.append('/app/framework')

# Import actual framework components
from database import get_session
from models import MotivationalPhrase


@pytest.fixture
def app():
    """Create and configure a Flask app instance for testing."""
    from flask import Flask

    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def db_session():
    """Create a database session for tests using the actual framework."""
    session = get_session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def clean_db(db_session):
    """Ensure clean database state for each test."""
    # Clear motivational phrases for clean tests
    db_session.query(MotivationalPhrase).delete()
    db_session.commit()
    yield db_session


@pytest.fixture
def sample_monster_data():
    """Sample monster data for testing."""
    return {
        "index": "ancient-red-dragon",
        "name": "Ancient Red Dragon",
        "size": "Gargantuan",
        "type": "dragon",
        "subtype": "",
        "alignment": "chaotic evil",
        "armor_class": 22,
        "hit_points": 546,
        "hit_dice": "28d20+252",
        "speed": {
            "walk": "40 ft.",
            "climb": "40 ft.",
            "fly": "80 ft."
        },
        "strength": 30,
        "dexterity": 14,
        "constitution": 29,
        "intelligence": 18,
        "wisdom": 15,
        "charisma": 23,
        "challenge_rating": 24,
        "proficiency_bonus": 7,
        "xp": 62000,
        "url": "/api/monsters/ancient-red-dragon"
    }


@pytest.fixture
def sample_monsters_list():
    """Sample monsters list for testing."""
    return {
        "count": 3,
        "results": [
            {
                "index": "dragon",
                "name": "Dragon",
                "url": "/api/monsters/dragon"
            },
            {
                "index": "orc",
                "name": "Orc",
                "url": "/api/monsters/orc"
            },
            {
                "index": "troll",
                "name": "Troll",
                "url": "/api/monsters/troll"
            }
        ]
    }


@pytest.fixture
def external_api_monster_response():
    """Mock response from external D&D API for a single monster."""
    return {
        "index": "orc",
        "name": "Orc",
        "size": "Medium",
        "type": "humanoid",
        "subtype": "orc",
        "alignment": "chaotic evil",
        "armor_class": 13,
        "hit_points": 15,
        "hit_dice": "2d8+6",
        "speed": {
            "walk": "30 ft."
        },
        "strength": 16,
        "dexterity": 12,
        "constitution": 16,
        "intelligence": 7,
        "wisdom": 11,
        "charisma": 10,
        "challenge_rating": 0.5,
        "proficiency_bonus": 2,
        "xp": 100,
        "url": "/api/monsters/orc"
    }


@pytest.fixture
def external_api_monsters_list_response():
    """Mock response from external D&D API for monsters list."""
    return {
        "count": 332,
        "results": [
            {"index": "aboleth", "name": "Aboleth",
             "url": "/api/monsters/aboleth"},
            {"index": "acolyte", "name": "Acolyte",
             "url": "/api/monsters/acolyte"},
            {"index": "adult-black-dragon", "name": "Adult Black Dragon",
             "url": "/api/monsters/adult-black-dragon"},
            {"index": "adult-blue-dragon", "name": "Adult Blue Dragon",
             "url": "/api/monsters/adult-blue-dragon"},
            {"index": "adult-brass-dragon", "name": "Adult Brass Dragon",
             "url": "/api/monsters/adult-brass-dragon"}
        ]
    }


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Automatically setup test environment for all tests."""
    # Set test environment variables
    monkeypatch.setenv("FLASK_ENV", "testing")
    monkeypatch.setenv("EXTERNAL_API_TIMEOUT", "1")  # Fast timeouts for tests
    monkeypatch.setenv("CACHE_TTL", "300")  # 5 minutes cache for tests


@pytest.fixture
def mock_external_api_success(monkeypatch, external_api_monster_response):
    """Mock successful external API response."""
    from unittest.mock import Mock

    mock_response = Mock()
    mock_response.json.return_value = external_api_monster_response
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200

    monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock_response)
    return mock_response


@pytest.fixture
def mock_external_api_failure(monkeypatch):
    """Mock external API failure."""
    import requests

    def mock_request_failure(*args, **kwargs):
        raise requests.ConnectionError("External API is down")

    monkeypatch.setattr("requests.get", mock_request_failure)


@pytest.fixture
def mock_external_api_timeout(monkeypatch):
    """Mock external API timeout."""
    import requests

    def mock_request_timeout(*args, **kwargs):
        raise requests.Timeout("Request timed out")

    monkeypatch.setattr("requests.get", mock_request_timeout)


@pytest.fixture
def mock_external_api_404(monkeypatch):
    """Mock external API 404 response."""
    import requests
    from unittest.mock import Mock

    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

    monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock_response)


@pytest.fixture
def monster_factory():
    """Factory for creating test monster data."""
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
def sample_motivational_phrase():
    """Sample motivational phrase for testing the existing framework."""
    return "You can do anything you set your mind to!"


@pytest.fixture
def performance_monitor():
    """Monitor test performance and log slow tests."""
    import time
    import warnings

    start_time = time.time()
    yield
    end_time = time.time()

    duration = end_time - start_time
    if duration > 1.0:  # Warn if test takes more than 1 second
        warnings.warn(f"Slow test detected: {duration:.2f} seconds")
