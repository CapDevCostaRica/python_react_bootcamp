# Exercise: Comprehensive Testing for D&D Monster Service

## Testing Workshop Exercise - Hands-On Learning

### Overview

In this workshop exercise, you'll practice implementing comprehensive tests for a D&D monster proxy caching service. This exercise covers unit tests, integration tests, fixtures, and mocking strategies using the materials already provided in your Docker environment.

### Workshop Structure

**No setup required!** All materials are ready in your Docker container:

```
/app/
├── examples/
│   └── test_examples.py      # 30 test examples (with intentional failures)
├── exercises/
│   └── testing_exercise.md   # This exercise guide
├── templates/
│   └── conftest_template.py  # Ready-to-use fixture templates
└── framework/                # Existing Flask framework
    ├── models.py            # Database models to test
    ├── database.py          # Database configuration
    └── ...
```

### Learning Objectives

Your testing practice will include:

1. **Understanding Test Failures** (interpreting pytest output)
2. **Fixture Implementation** (using conftest_template.py)
3. **Unit Tests** (test individual functions/methods)
4. **Integration Tests** (test API endpoints and database operations)
5. **Mocking Strategy** (for external dependencies)
6. **Error Handling Tests** (for failure scenarios)

### Part 1: Understanding the Current Test Examples

First, examine the existing test examples to understand the testing patterns:

```bash
# In your Docker container (/app)
pytest examples/test_examples.py -v

# You'll see 30 failing tests - this is expected!
# These failures teach you what needs to be implemented
```

#### Key Learning Points from the Failures:

1. **Fixture Errors**: `fixture 'client' not found`, `fixture 'db_session' not found`

   - **Solution**: Copy fixtures from `templates/conftest_template.py`

2. **Import Errors**: `ModuleNotFoundError: No module named 'your_app'`
   - **Solution**: Replace placeholder imports with actual app imports

### Part 2: Setup Test Infrastructure

#### Step 1: Create Your Test Directory

```bash
# Create a test directory for your practice
mkdir -p my_testing_practice/tests
cd my_testing_practice/tests
```

#### Step 2: Copy and Customize Fixtures

```bash
# Copy the template fixtures
cp /app/templates/conftest_template.py conftest.py
```

#### Edit conftest.py to match your app structure:

```python
import pytest
import tempfile
import os
import sys

# Add the framework to Python path
sys.path.append('/app/framework')

from database import get_session, DATABASE_URL
from models import Base

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Use the existing framework structure
    from flask import Flask

    app = Flask(__name__)
    app.config['TESTING'] = True

    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def db_session():
    """Create a database session for tests."""
    session = get_session()
    yield session
    session.close()

@pytest.fixture
def sample_monster_data():
    """Sample monster data for testing."""
    return {
        "index": "dragon",
        "name": "Ancient Red Dragon",
        "type": "dragon",
        "challenge_rating": 24,
        "url": "/api/monsters/ancient-red-dragon"
    }
```

### Part 3: Hands-On Testing Practice

#### Step 3: Fix One Test at a Time

Start with a simple test from the examples:

```bash
# Run just one test to see the specific error
pytest examples/test_examples.py::TestMonsterModel::test_monster_string_representation -v
```

#### Step 4: Create Your First Working Test

Create `my_testing_practice/tests/test_simple.py`:

```python
import sys
sys.path.append('/app/framework')

def test_basic_functionality():
    """A simple test to verify testing setup works."""
    from models import MotivationalPhrase

    phrase = MotivationalPhrase(phrase="Testing is awesome!")
    assert phrase.phrase == "Testing is awesome!"
    assert str(phrase) == "Testing is awesome!"

def test_database_connection(db_session):
    """Test that database connection works."""
    from models import MotivationalPhrase

    # Create a test phrase
    phrase = MotivationalPhrase(phrase="Test phrase")
    db_session.add(phrase)
    db_session.commit()

    # Query it back
    found_phrase = db_session.query(MotivationalPhrase).filter_by(phrase="Test phrase").first()
    assert found_phrase is not None
    assert found_phrase.phrase == "Test phrase"
```

#### Step 5: Practice with Mock Data

Create `my_testing_practice/tests/test_with_fixtures.py`:

```python
import sys
sys.path.append('/app/framework')

def test_sample_data_fixture(sample_monster_data):
    """Test using the sample data fixture."""
    assert sample_monster_data["name"] == "Ancient Red Dragon"
    assert sample_monster_data["challenge_rating"] == 24
    assert "dragon" in sample_monster_data["index"]

def test_database_with_sample_data(db_session, sample_monster_data):
    """Test database operations with sample data."""
    from models import MotivationalPhrase

    # Use sample data to create a motivational phrase about dragons
    dragon_phrase = f"Be mighty like a {sample_monster_data['name']}!"

    phrase = MotivationalPhrase(phrase=dragon_phrase)
    db_session.add(phrase)
    db_session.commit()

    # Verify it was saved
    found = db_session.query(MotivationalPhrase).filter_by(phrase=dragon_phrase).first()
    assert found is not None
```

### Part 4: Running Your Practice Tests

#### Test Your Implementation

```bash
# Run your practice tests
cd /app/my_testing_practice
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing

# Run specific test files
pytest tests/test_simple.py -v
pytest tests/test_with_fixtures.py -v
```

#### Compare with Examples

```bash
# Now try running the workshop examples again
cd /app
pytest examples/test_examples.py::TestMonsterSchemas::test_monster_list_request_schema_valid -v

# See how your understanding has improved!
```

### Part 5: Advanced Practice (Optional)

For students who want to go further:

#### Create API Tests

```python
# my_testing_practice/tests/test_api_practice.py
import json
import sys
sys.path.append('/app/framework')

def test_flask_app_creation(client):
    """Test that we can create a Flask test client."""
    # Simple endpoint test
    response = client.get('/')
    # The response might be 404 since we don't have routes set up
    # but the client should work
    assert response is not None

def test_json_handling(client):
    """Practice JSON request/response handling."""
    test_data = {"message": "Hello, testing!"}

    # This will likely return an error since we don't have this endpoint
    # but it's good practice for understanding the pattern
    response = client.post('/test',
                          data=json.dumps(test_data),
                          content_type='application/json')

    # Just verify we can make the request
    assert response is not None
```

#### Practice Mocking

```python
# my_testing_practice/tests/test_mocking_practice.py
from unittest.mock import Mock, patch
import requests

def test_mock_external_api():
    """Practice mocking external API calls."""
    # Create a mock response
    mock_response = Mock()
    mock_response.json.return_value = {"name": "Test Monster", "index": "test"}
    mock_response.status_code = 200

    # Test that we can work with mock data
    assert mock_response.json()["name"] == "Test Monster"
    assert mock_response.status_code == 200

@patch('requests.get')
def test_mock_requests(mock_get):
    """Practice patching requests.get."""
    # Configure the mock
    mock_response = Mock()
    mock_response.json.return_value = {"count": 5, "results": []}
    mock_get.return_value = mock_response

    # Make a request (this will use our mock)
    response = requests.get("https://example.com/api")

    # Verify the mock was used
    assert response.json()["count"] == 5
    mock_get.assert_called_once_with("https://example.com/api")
```

### Workshop Completion Goals

By the end of this exercise, you should understand:

1. **✅ How to read pytest output** and interpret test failures
2. **✅ How to use fixtures** for test setup and data
3. **✅ How to write unit tests** for individual functions
4. **✅ How to mock external dependencies**
5. **✅ How to organize test files** and structure
6. **✅ How to run tests** with different options

### Next Steps

After completing this workshop:

1. **Review the examples** in `/app/examples/test_examples.py` with your new understanding
2. **Try fixing some of the failing tests** by replacing `your_app` imports
3. **Experiment with different fixture combinations**
4. **Practice writing tests** for your own code

### Resources

- **Examples**: `/app/examples/test_examples.py` - 30 comprehensive test examples
- **Templates**: `/app/templates/conftest_template.py` - Ready-to-use fixtures
- **Framework**: `/app/framework/` - Existing models and database setup
- **pytest documentation**: https://docs.pytest.org/
- **Flask testing**: https://flask.palletsprojects.com/en/2.3.x/testing/
