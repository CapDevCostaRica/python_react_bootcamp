"""
Configuration file for pytest with comprehensive test fixtures.
This file provides all necessary fixtures for testing Flask applications
with SQLAlchemy, including database setup, test client, sample data, and API mocking.
"""
import pytest
import sys
import os
import time
import warnings

# Step 6: Add Monster model imports here
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'examples'))
from test_examples import Monster, Base

# Import our test utilities
from test_config import TestConfig
from test_factories import TestDataFactory, MockAPIResponseFactory

# Step 10: Add shared database session variable here
_shared_session = None


def get_db_session():
    """Get the shared database session for Flask routes."""
    return _shared_session


@pytest.fixture
def app():
    """Create and configure a Flask app instance for testing."""
    from flask import Flask, request, jsonify

    app = Flask(__name__)
    app.config.update({
        'TESTING': TestConfig.FLASK_TESTING,
        'WTF_CSRF_ENABLED': TestConfig.FLASK_WTF_CSRF_ENABLED,
        'SECRET_KEY': TestConfig.FLASK_SECRET_KEY
    })

    # Step 11: Add Flask routes here
    @app.route('/monsters', methods=['POST'])
    def monsters_list():
        """Mock monsters list endpoint."""
        try:
            # Handle POST requests for monster lists
            data = request.get_json()
            if not data or data.get("resource") != "monsters":
                return jsonify({"error": "Invalid resource"}), 400

            # Return monsters from database or fallback mock data
            session = get_db_session()
            if session:
                monsters = session.query(Monster).all()
                if monsters:
                    results = []
                    for monster in monsters:
                        results.append({
                            "index": monster.index,
                            "name": monster.name,
                            "url": f"/api/monsters/{monster.index}"
                        })
                    return jsonify({"count": len(results), "results": results})

            # Fallback mock data when no cached data exists
            mock_data = {
                "count": 2,
                "results": [
                    {"index": "dragon", "name": "Dragon", "url": "/api/monsters/dragon"},
                    {"index": "orc", "name": "Orc", "url": "/api/monsters/orc"}
                ]
            }
            return jsonify(mock_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/monster', methods=['POST'])
    def monster_get():
        """Mock monster get endpoint."""
        try:
            # Handle POST requests for single monsters
            data = request.get_json()
            if not data or "monster_index" not in data:
                return jsonify({"error": "monster_index required"}), 400

            monster_index = data["monster_index"]

            # Return monster from database or mock data
            session = get_db_session()
            if session:
                monster = session.query(Monster).filter_by(index=monster_index).first()
                if monster:
                    # Return full monster data from database
                    result = {
                        "index": monster.index,
                        "name": monster.name,
                    }
                    # Include all data from monster.data
                    if monster.data:
                        result.update(monster.data)
                    return jsonify(result)

            # Mock response if not found in database
            return jsonify({
                "index": monster_index,
                "name": f"Mock {monster_index.title()}",
                "data": {"type": "mock"}
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def db_session():
    """Create a database session for tests using SQLAlchemy."""
    global _shared_session

    # Import SQLAlchemy components
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Create in-memory SQLite engine
    engine = create_engine('sqlite:///:memory:', echo=False)

    # Create all tables using Base.metadata.create_all()
    Base.metadata.create_all(engine)

    # Create and return session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Set global _shared_session for Flask routes
    _shared_session = session

    yield session

    session.rollback()
    session.close()
    _shared_session = None


@pytest.fixture
def clean_db(db_session):
    """Ensure clean database state for each test."""
    # Clear all Monster data for clean tests
    db_session.query(Monster).delete()
    db_session.commit()
    yield db_session


# Step 15: Add sample test data fixtures
# Step 13: Add sample test data
@pytest.fixture
def sample_monster_data():
    """Provide sample monster data for testing using the factory."""
    return TestDataFactory.create_monster_data()

@pytest.fixture
def sample_monster_variations():
    """Provide multiple monster variations for comprehensive testing."""
    return TestDataFactory.create_monster_variations()

@pytest.fixture
def external_api_monster_response():
    """Provide sample external API response using the factory."""
    return TestDataFactory.create_external_api_response()

@pytest.fixture
def monster_factory():
    """Enhanced factory for creating test monster data with better flexibility."""
    def _create_monster(index=None, name=None, **kwargs):
        import uuid
        # Generate unique test monster data
        if index is None:
            index = f"test-monster-{str(uuid.uuid4())[:8]}"
        if name is None:
            name = f"Test Monster {index.title()}"

        # Use TestDataFactory as base, then add D&D specific fields
        base_data = TestDataFactory.create_monster_data(name=name, **kwargs)
        
        # Add D&D specific fields
        dnd_fields = {
            "index": index,
            "type": kwargs.get("type", "beast"),
            "challenge_rating": kwargs.get("challenge_rating", 1),
            "hit_points": kwargs.get("hit_points", 20),
            "armor_class": kwargs.get("armor_class", 12)
        }
        
        base_data.update(dnd_fields)
        return base_data
    return _create_monster

# Step 16: Add external API mocking fixtures
@pytest.fixture
def mock_external_api_success(monkeypatch, external_api_monster_response):
    """Mock successful external API response using the factory."""
    mock_response = MockAPIResponseFactory.create_success_response(external_api_monster_response)

    def mock_request(*args, **kwargs):
        return mock_response

    monkeypatch.setattr("requests.get", mock_request)
    return mock_response

@pytest.fixture
def mock_external_api_failure(monkeypatch):
    """Mock external API connection failure."""
    mock_request = MockAPIResponseFactory.create_connection_error_mock()
    monkeypatch.setattr("requests.get", mock_request)

@pytest.fixture
def mock_external_api_timeout(monkeypatch):
    """Mock external API timeout."""
    mock_request = MockAPIResponseFactory.create_timeout_mock()
    monkeypatch.setattr("requests.get", mock_request)

@pytest.fixture
def mock_external_api_404(monkeypatch):
    """Mock external API 404 response using the factory."""
    mock_response = MockAPIResponseFactory.create_404_response()

    def mock_request_404(*args, **kwargs):
        return mock_response

    monkeypatch.setattr("requests.get", mock_request_404)

# Step 18: Add performance monitoring
@pytest.fixture
def performance_monitor():
    """Monitor test performance and log slow tests."""
    start_time = time.time()
    yield
    duration = time.time() - start_time

    # Warn about slow tests using configurable threshold
    if duration > TestConfig.PERFORMANCE_THRESHOLD:
        warnings.warn(f"Slow test detected: {duration:.2f}s execution time", UserWarning)

# Step 19: Add automatic test environment setup
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Automatically setup test environment for all tests."""
    # Set environment variables for testing using configuration
    monkeypatch.setenv("TESTING", TestConfig.TESTING_ENV)
    monkeypatch.setenv("CACHE_TTL", str(TestConfig.CACHE_TTL))
    monkeypatch.setenv("LOG_LEVEL", TestConfig.LOG_LEVEL)
