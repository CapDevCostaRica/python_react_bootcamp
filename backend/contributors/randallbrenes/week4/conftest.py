# conftest.py - Testing Workshop Student Template
# 🎯 TASK: Build this file step-by-step following the STUDENT_WORKSHOP_GUIDE.md

import pytest
import sys

# Add framework to Python path for workshop
sys.path.append('/app/framework')

# Import actual framework components
sys.path.append('/app/examples')
from test_examples import Monster, Base

# TODO Step 10: Add shared database session variable here
_shared_session = None

def get_db_session():
    """Get the shared database session for Flask routes."""
    global _shared_session

    return _shared_session

@pytest.fixture
def db_session():
    """Create a database session for tests using SQLAlchemy."""
    global _shared_session

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    # Create in-memory SQLite database
    engine = create_engine(
        'sqlite:///:memory:',
        echo=False,
        poolclass=StaticPool,
        connect_args={'check_same_thread': False}
    )

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Share session with Flask app
    _shared_session = session

    yield session

    # Cleanup
    session.rollback()
    session.close()
    _shared_session = None

@pytest.fixture
def app(sample_monster_data, db_session):
    """Create and configure a Flask app instance for testing."""
    from flask import Flask, jsonify, request

    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })

    @app.route('/monsters', methods=['POST'])
    def monsters_list():
        """Mock monsters list endpoint - handles POST requests for monster lists."""
        try:
            data = request.get_json()

            # Validate required fields
            if not data or "resource" not in data:
                return jsonify({"error": "Missing resource field"}), 400

            if data["resource"] != "monsters":
                return jsonify({"error": "Invalid resource"}), 400

            # Query database for monsters using shared session
            session = db_session

            if session:
                monsters = session.query(Monster).all()
                if(len(monsters) == 0):
                    return jsonify({
                        "count": 2,
                        "results": [
                            {"index": "dragon", "name": "Dragon", "url": "/api/monsters/dragon"},
                            {"index": "orc", "name": "Orc", "url": "/api/monsters/orc"}
                        ]
                    })
                else:
                    return jsonify({
                        "count": len(monsters),
                        "results": [
                            {"index": m.index, "name": m.name, "url": f"/api/monsters/{m.index}"}
                            for m in monsters
                        ]
                    })
            else:
                # Fallback mock response when no database session
                return jsonify({
                    "count": 2,
                    "results": [
                        {"index": "dragon", "name": "Dragon", "url": "/api/monsters/dragon"},
                        {"index": "orc", "name": "Orc", "url": "/api/monsters/orc"}
                    ]
                })
        except Exception as e:
            return jsonify({"error": "Invalid JSON"}), 400

    @app.route('/monster', methods=['POST'])
    def monster_get():
        """Mock monster get endpoint - handles POST requests for single monsters."""
        try:
            data = request.get_json()
            if not data or "monster_index" not in data:
                return jsonify({"error": "Missing monster_index field"}), 400

            monster_index = data["monster_index"]

            # Try to find monster in database first
            session = get_db_session()
            if session:
                monster = session.query(Monster).filter_by(index=monster_index).first()
                if monster:
                    result = {
                        "index": monster.index,
                        "name": monster.name,
                        **monster.data  # Include additional monster data
                    }
                    return jsonify(result)

            # Return mock data if not found in database
            return jsonify(sample_monster_data)
        except Exception as e:
            print("ERROR!!! ")
            print(str(e))
            return jsonify({"error": "Invalid JSON"}), 400

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def db_session():
    """Create a database session for tests using SQLAlchemy."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    # Create in-memory SQLite database for testing
    engine = create_engine(
        'sqlite:///:memory:',
        echo=False,  # Set to True to see SQL queries
        poolclass=StaticPool,
        connect_args={'check_same_thread': False}
    )

    # Create all tables (including Monster table)
    Base.metadata.create_all(engine)

    # Create session to interact with database
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session  # This gives the session to your test

    # Cleanup after test
    session.rollback()
    session.close()


@pytest.fixture
def clean_db(db_session):
    """Ensure clean database state for each test."""
    # Clear motivational phrases for clean tests
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
        "challenge_rating": 24,
        "url": "/api/monsters/ancient-red-dragon"
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
        "challenge_rating": 0.5,
        "url": "/api/monsters/orc"
    }

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
def mock_external_api_success(monkeypatch, external_api_monster_response):
    """Mock successful external API response."""
    from unittest.mock import Mock

    mock_response = Mock()
    mock_response.json.return_value = external_api_monster_response
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200

    # Replace the real requests.get with our mock
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

# TODO Step 18: Add performance monitoring
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

# TODO Step 19: Add automatic test environment setup
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Automatically setup test environment for all tests."""
    # Set test environment variables
    monkeypatch.setenv("FLASK_ENV", "testing")
    monkeypatch.setenv("EXTERNAL_API_TIMEOUT", "1")  # Fast timeouts for tests
    monkeypatch.setenv("CACHE_TTL", "300")  # 5 minutes cache for tests

