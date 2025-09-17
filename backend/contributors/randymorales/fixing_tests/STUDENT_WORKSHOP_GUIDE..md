# 🎯 Testing Workshop: Complete Step-by-Step Student Guide

**Workshop Goal:** Transform 14 failing tests into 14 passing tests by building a complete testing environment step by step.

---

## 📋 **Workshop Overview**

You'll learn to:

- ✅ Set up pytest fixtures and configuration
- ✅ Mock external APIs and services
- ✅ Test database operations with SQLAlchemy
- ✅ Build Flask API endpoints for testing
- ✅ Handle error scenarios and edge cases
- ✅ Monitor test performance and concurrency

---

## 🚀 **Phase 1: Environment Setup (10 minutes)**

### **Step 1: Enter the Workshop Environment**

```bash
# Start Docker and enter the container
docker compose up -d
docker ps -a
docker exec -it python_react_bootcamp-flask_app-1 bash

# Navigate to workshop directory
cd ~/capdevcr/python_react_bootcamp/backend/randymorales/fixing_tests

```

**Expected Output:** You should see `test_examples.py` and `STUDENT_WORKSHOP_GUIDE.md` but NO `conftest.py` yet.
**What's happening:** The tests need fixtures (test setup code) that we haven't created yet.

---

## 🔧 **Phase 2: Create Testing Foundation (15 minutes)**

### **Step 2: Copy the Configuration Template**

**TASK:** Copy the template configuration to create your working test setup:

```bash
cp conftest_template.py conftest.py
```

**What you just did:**

- Created `conftest.py` - the heart of pytest configuration
- This file contains "fixtures" - reusable test setup code
- Fixtures provide consistent testing environment for all tests

### **Step 3: Understand Your Starting Point**

Open `conftest.py` and examine what the template provides:

```python
@pytest.fixture
def app():
    """Creates a Flask app for testing"""

@pytest.fixture
def client(app):
    """Creates an HTTP client to test your API"""

@pytest.fixture
def db_session():
    """Creates database access for tests"""

@pytest.fixture
def clean_db(db_session):
    """Ensures clean data between tests"""
```

**Learning moment:** Each `@pytest.fixture` is a function that sets up something your tests need.

### **Step 4: Test Your Foundation**

```bash
pytest -v
```

**Expected:** Some tests should start passing, but most will still fail because we need more fixtures.

---

## 🎯 **Phase 3: Add Monster Model Support (20 minutes)**

### **Step 5: Understanding What Tests Expect**

Look at the failing tests. They expect:

- A `Monster` model (database table)
- API endpoints: `/monsters` and `/monster`
- Database sessions that can store/retrieve monsters

### **Step 6: Add Monster Model Integration**

**TASK:** Add these imports to the top of your `conftest.py`:

```python
# Add these imports at the top of conftest.py (after the existing imports)
import sys
sys.path.append('/app/examples')
from test_examples import Monster, Base
```

**What this does:**

- Imports the `Monster` class from the test file
- Imports `Base` (SQLAlchemy's table foundation)
- Makes these available to your fixtures

### **Step 7: Create Real Database Support**

**TASK:** Replace the basic `db_session` fixture with this complete version:

```python
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
```

**Learning moment:**

- `sqlite:///:memory:` creates a temporary database that exists only in RAM
- Each test gets a fresh, empty database
- `Base.metadata.create_all()` creates the Monster table structure

### **Step 8: Test Database Integration**

```bash
pytest -v -k "test_create_monster"
```

**Expected:** Monster creation tests should now pass!

---

## 🌐 **Phase 4: Build Mock API Endpoints (25 minutes)**

### **Step 9: Understanding API Testing Needs**

The tests expect these HTTP endpoints:

- `POST /monsters` - Get list of all monsters
- `POST /monster` - Get a specific monster by index

### **Step 10: Add Shared Database Session**

**TASK:** Add this global variable and helper function to your `conftest.py`:

```python
# Add this after your imports, before the fixtures
_shared_session = None

def get_db_session():
    """Get the shared database session for Flask routes."""
    global _shared_session
    return _shared_session
```

**Why:** Flask routes need access to the same database session your tests use.

### **Step 11: Enhance Your Flask App Fixture**

**TASK:** Replace your `app` fixture with this enhanced version:

```python
@pytest.fixture
def app():
    """Create and configure a Flask app instance for testing."""
    from flask import Flask, request, jsonify

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
            else:
                # Fallback mock response when no database session
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
```

**Learning moments:**

- Flask routes handle HTTP requests (like a web API)
- `request.get_json()` gets data sent to the API
- `jsonify()` returns JSON responses
- Error handling returns appropriate HTTP status codes (400, 500, etc.)

### **Step 12: Connect Database to Flask App**

**TASK:** Update your `db_session` fixture to share the session with Flask:

```python
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
```

### **Step 13: Test Your API Endpoints**

```bash
pytest -v -k "test_monster_list"
```

**Expected:** Monster list API tests should now pass!

```bash
pytest -v -k "test_monster_get"
```

**Expected:** Monster get API tests should start passing!

---

## 🧪 **Phase 5: Add External API Mocking (20 minutes)**

### **Step 14: Understanding External API Testing**

Some tests simulate calling external APIs (like a D&D monster database). We need to mock these calls to:

- Make tests run fast (no real network calls)
- Make tests reliable (don't depend on external services)
- Test different scenarios (success, failure, timeout)

### **Step 15: Add Sample Test Data Fixtures**

**TASK:** Add these fixtures to your `conftest.py`:

```python
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
```

**Learning moment:**

- `monster_factory` is a "factory pattern" - it creates test data on demand
- Factories let you customize test data for specific scenarios

### **Step 16: Add External API Mocking Fixtures**

**TASK:** Add these mocking fixtures:

```python
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
```

**Learning moments:**

- `monkeypatch` replaces real functions with fake ones during tests
- `Mock()` creates fake objects that behave like real ones
- We can simulate different API responses (success, failure, timeout, 404)

### **Step 17: Test External API Mocking**

```bash
pytest -v -k "external_api"
```

**Expected:** External API tests should now pass!

---

## ⚡ **Phase 6: Performance and Advanced Features (15 minutes)**

### **Step 18: Add Performance Monitoring**

**TASK:** Add this performance monitoring fixture:

```python
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
```

### **Step 19: Add Automatic Test Environment Setup**

**TASK:** Add this auto-setup fixture:

```python
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Automatically setup test environment for all tests."""
    # Set test environment variables
    monkeypatch.setenv("FLASK_ENV", "testing")
    monkeypatch.setenv("EXTERNAL_API_TIMEOUT", "1")  # Fast timeouts for tests
    monkeypatch.setenv("CACHE_TTL", "300")  # 5 minutes cache for tests
```

**Learning moment:** `autouse=True` means this fixture runs automatically for every test.

### **Step 20: Test Performance Features**

```bash
pytest -v -k "performance"
```

---

## 🎯 **Phase 7: Final Integration and Verification (10 minutes)**

### **Step 21: Run Complete Test Suite**

```bash
pytest -v
```

**Expected Result:** All 14 tests should now pass! 🎉

### **Step 22: Analyze What You Built**

Look at your `conftest.py` file. You've created:

1. **Database Integration** - In-memory SQLite with Monster model
2. **Flask API Endpoints** - Mock HTTP endpoints for testing
3. **External API Mocking** - Simulate external service calls
4. **Test Data Factories** - Generate test data on demand
5. **Performance Monitoring** - Track slow tests
6. **Error Handling** - Test various failure scenarios

### **Step 23: Understanding Test Categories**

Your 14 tests cover:

**TestMonsterModel** (4 tests)

- ✅ `test_create_monster_success` - Basic object creation
- ✅ `test_monster_unique_constraint` - Database constraints
- ✅ `test_monster_required_fields` - Field validation
- ✅ `test_monster_string_representation` - Object display

**TestMonsterSchemas** (7 tests)

- ✅ `test_monster_list_request_schema_valid` - Valid schema requests
- ✅ `test_monster_list_request_schema_invalid_resource` - Error handling
- ✅ `test_monster_get_request_schema_valid` - Valid get requests
- ✅ `test_monster_get_request_schema_missing_index` - Missing field validation
- ✅ `test_monster_get_request_schema_invalid_index` - Invalid data validation (3 parametrized cases)

**TestMonsterAPI** (3 tests)

- ✅ `test_monsters_list_from_cache` - Database integration with API
- ✅ `test_monsters_list_from_external_api` - External API mocking
- ✅ `test_monster_get_from_cache` - Single monster retrieval

---

## 🎓 **Learning Outcomes**

By completing this workshop, you've learned:

### **Core Testing Concepts:**

- ✅ **Pytest fixtures** - Reusable test setup code
- ✅ **Test isolation** - Each test runs independently
- ✅ **Mocking** - Simulating external dependencies
- ✅ **Parametrized tests** - Running same test with different data

### **Database Testing:**

- ✅ **In-memory databases** - Fast, isolated test databases
- ✅ **SQLAlchemy integration** - ORM testing patterns
- ✅ **Transaction rollback** - Clean state between tests

### **API Testing:**

- ✅ **Flask test client** - Testing HTTP endpoints
- ✅ **JSON request/response** - API communication patterns
- ✅ **Error handling** - Testing failure scenarios

### **Advanced Patterns:**

- ✅ **Factory pattern** - Generating test data
- ✅ **Monkeypatching** - Replacing functions during tests
- ✅ **Performance monitoring** - Tracking test speed
- ✅ **Environment setup** - Configuring test conditions

---

## 🔧 **Common Issues and Solutions**

### **Import Errors**

```bash
# If you get "No module named..." errors:
export PYTHONPATH=/app:/app/framework:/app/examples
```

### **Database Errors**

```python
# If Monster table doesn't exist, ensure this is in db_session:
Base.metadata.create_all(engine)
```

### **Mock Not Working**

```python
# Ensure you're using the right fixture in your test:
def test_something(mock_external_api_success):
    # Your test code here
```

### **Slow Tests**

```bash
# Run with performance monitoring:
pytest -v -s  # -s shows warnings including performance warnings
```

---

## 🎉 **Congratulations!**

You've successfully:

- 🏗️ Built a complete testing infrastructure from scratch
- 🧪 Created 13 different pytest fixtures
- 🌐 Mocked external API calls and database interactions
- ⚡ Implemented performance monitoring and error handling
- 🎯 Made 14 tests pass by understanding and fixing each failure

**This hands-on experience gives you the foundation to test any Python application professionally!**

---

## 🚀 **Next Steps**

Apply these patterns to your own projects:

1. **Start with fixtures** - Set up your test infrastructure first
2. **Mock external dependencies** - Keep tests fast and reliable
3. **Use factories for test data** - Generate what you need, when you need it
4. **Monitor performance** - Keep tests running quickly
5. **Test error scenarios** - Don't just test the happy path

**Happy testing!** 🐍✨