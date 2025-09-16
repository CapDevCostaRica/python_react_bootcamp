# conftest.py - Testing Workshop Student Template
# 🎯 TASK: Build this file step-by-step following the STUDENT_WORKSHOP_GUIDE.md

import pytest
import sys

# Add framework to Python path for workshop
sys.path.append('/app/framework')

# Import actual framework components
from models import MotivationalPhrase

# TODO Step 6: Add Monster model imports here
# sys.path.append('/app/examples')
# from test_examples import Monster, Base

# TODO Step 10: Add shared database session variable here
# _shared_session = None


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

    # TODO Step 11: Add Flask routes here
    # @app.route('/monsters', methods=['POST'])
    # def monsters_list():
    #     """Mock monsters list endpoint."""
    #     # Handle POST requests for monster lists
    #     # Validate JSON: {"resource": "monsters"}
    #     # Return monsters from database or fallback mock data
    #     pass

    # @app.route('/monster', methods=['POST'])
    # def monster_get():
    #     """Mock monster get endpoint."""
    #     # Handle POST requests for single monsters
    #     # Validate JSON: {"monster_index": "dragon"}
    #     # Return monster from database or mock data
    #     pass

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def db_session():
    """Create a database session for tests using SQLAlchemy."""
    # TODO Step 7-8: Replace this basic session with SQLAlchemy setup
    # 1. Import SQLAlchemy components
    # 2. Create in-memory SQLite engine
    # 3. Create all tables using Base.metadata.create_all()
    # 4. Create and return session
    # 5. Set global _shared_session for Flask routes

    from database import get_session
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
