# conftest.py - Testing Workshop Student Template
# 🎯 TASK: Build this file step-by-step following the STUDENT_WORKSHOP_GUIDE.md

import pytest
import sys

# Add framework to Python path for workshop
sys.path.append('/app/framework')

# Import actual framework components
from models import MotivationalPhrase

# TODO Step 6: Add Monster model imports here
sys.path.append('/app/examples')
from test_examples import Monster, Base

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from unittest.mock import Mock

_shared_session = None

# TODO Step 10: Add shared database session variable here
@pytest.fixture
def db_session():
    """SQLite en memoria + tablas creadas con Base.metadata (incluye Monster)."""
    global _shared_session

    engine = create_engine(
        'sqlite:///:memory:',
        echo=False,
        poolclass=StaticPool,
        connect_args={'check_same_thread': False}
    )
    Base.metadata.create_all(engine)

    try:
        MotivationalPhrase.__table__.create(bind=engine, checkfirst=True)
    except Exception:
        pass

    Session = sessionmaker(bind=engine, expire_on_commit=False)
    session = Session()

    _shared_session = session
    yield session

    session.rollback()
    session.close()
    _shared_session = None


@pytest.fixture
def app(db_session):
    """Create and configure a Flask app instance for testing."""
    from flask import Flask, request, jsonify
    import requests

    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })

    @app.route('/monsters', methods=['POST'])
    def monsters_list():
        payload = request.get_json(silent=True) or {}
        if payload.get("resource") != "monsters":
            return jsonify({"errors": {"resource": ["Must be one of: monsters"]}}), 422

        monsters = db_session.query(Monster).all()
        if monsters:
            return jsonify({
                "count": len(monsters),
                "results": [
                    {"index": m.index, "name": m.name, "url": f"/api/monsters/{m.index}"}
                    for m in monsters
                ]
            }), 200
        
        provider = app.config.get("MONSTER_LIST_PROVIDER")
        if provider is not None:
            data = provider()
        else:
            data = {
                "count": 2,
                "results": [
                    {"index": "dragon", "name": "Dragon", "url": "/api/monsters/dragon"},
                    {"index": "orc", "name": "Orc", "url": "/api/monsters/orc"},
                ]
            }
        return jsonify(data), 200


    @app.route('/monster', methods=['POST'])
    def monster_get():
        payload = request.get_json(silent=True) or {}
        idx = payload.get("monster_index")

        if idx is None or not str(idx).strip() or len(str(idx)) > 100:
            return jsonify({"errors": {"monster_index": ["Invalid"]}}), 422

        m = db_session.query(Monster).filter_by(index=idx).first()
        if not m:
            return jsonify({"error": "not found"}), 404

        body = {"index": m.index, "name": m.name}
        if isinstance(m.data, dict):
            body.update(m.data)
        return jsonify(body), 200

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def clean_db(db_session):
    """Ensure clean database state for each test."""
    # Clear motivational phrases for clean tests
    db_session.query(MotivationalPhrase).delete()
    db_session.commit()
    yield db_session


# TODO Step 15: Add sample test data fixtures
@pytest.fixture
def sample_monster_data():
    return {
        "index": "ancient-red-dragon",
        "name": "Ancient Red Dragon",
        "type": "dragon",
        "challenge_rating": 24,
        "size": "Gargantuan",
    }

# TODO Step 15: Add sample test data fixtures
# @pytest.fixture
# def sample_monster_data():
#     """Sample monster data for testing."""
#     return {
#         "index": "ancient-red-dragon",
#         "name": "Ancient Red Dragon",
#         # Add more realistic monster data...
#     }

# TODO Step 15: Add monster factory fixture
# @pytest.fixture
# def monster_factory():
#     """Factory for creating test monster data."""
#     def _create_monster(index=None, name=None, **kwargs):
#         # Generate unique test monster data
#         # Allow customization through kwargs
#         pass
#     return _create_monster

# TODO Step 16: Add external API mocking fixtures
# @pytest.fixture
# def mock_external_api_success(monkeypatch, external_api_monster_response):
#     """Mock successful external API response."""
#     # Use monkeypatch to replace requests.get
#     # Return mock response object with .json() and .raise_for_status()
#     pass

# @pytest.fixture
# def mock_external_api_failure(monkeypatch):
#     """Mock external API failure."""
#     # Simulate ConnectionError from requests
#     pass

# @pytest.fixture
# def mock_external_api_timeout(monkeypatch):
#     """Mock external API timeout."""
#     # Simulate Timeout from requests
#     pass

# @pytest.fixture
# def mock_external_api_404(monkeypatch):
#     """Mock external API 404 response."""
#     # Simulate HTTPError 404 response
#     pass

# TODO Step 18: Add performance monitoring
# @pytest.fixture
# def performance_monitor():
#     """Monitor test performance and log slow tests."""
#     # Track test execution time
#     # Warn about slow tests (>1 second)
#     pass

# TODO Step 19: Add automatic test environment setup
# @pytest.fixture(autouse=True)
# def setup_test_environment(monkeypatch):
#     """Automatically setup test environment for all tests."""
#     # Set environment variables for testing
#     # Configure timeouts and cache settings
#     pass

# 🎯 LEARNING GOALS:
# By the end of this workshop, you'll understand:
# ✅ How to create pytest fixtures for reusable test setup
# ✅ How to mock external dependencies (APIs, databases)
# ✅ How to test Flask applications with HTTP endpoints
# ✅ How to use in-memory databases for fast, isolated tests
# ✅ How to handle error scenarios in your tests
# ✅ How to monitor test performance and optimize slow tests

# 📚 REFERENCE:
# - Follow STUDENT_WORKSHOP_GUIDE.md for detailed step-by-step instructions
# - Check INSTRUCTOR_CHECKLIST.md if you get stuck
# - Your instructor has the complete solution for reference

