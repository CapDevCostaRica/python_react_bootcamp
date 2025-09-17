"""
Example tests for D&D Monster Service - Python Testing Workshop

🎯 GOAL: Fix all 30 failing tests by building proper fixtures in conftest.py
📚 Workshop Focus: SQLAlchemy, Flask routes, Marshmallow validation, threading

Pro tip: Run `pytest -v` to see which tests pass/fail, then follow STUDENT_WORKSHOP_GUIDE.md!
"""

import pytest
import json
import time
import threading
from unittest.mock import Mock, patch
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError
import requests

# Mock Monster model for demonstration purposes
from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class Monster(Base):
    """Mock Monster model for testing workshop - now SQLAlchemy compatible."""
    __tablename__ = 'monsters'

    id = Column(Integer, primary_key=True)
    index = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    data = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, index=None, name=None, data=None):
        # Validate presence of required fields: 'index' and 'name'.
        if index is None: raise ValueError("index is required")
        if name is None: raise ValueError("name is required")

        self.index = index
        self.name = name
        self.data = data or {}

    def __str__(self):
        # Implement string representation
        # HINT: Should return "Name (index)" format
        return f"{self.name} ({self.index})"

# Mock Schema classes for demonstration
class MonsterListRequestSchema:
    """Mock schema for monster list requests."""
    def load(self, data):
        # Validate 'resource' field exists and equals 'monsters'.

        if "resource" not in data:
            return ValidationError("The key 'resource' is required.")
        if data.get('resource') != 'monsters':
            raise ValidationError("Must be one of: monsters")
            
        return data  # This passes validation!


class MonsterGetRequestSchema:
    """Mock schema for monster get requests."""
    def load(self, data):
        # Add validation for monster get requests
        # HINT: Check for "monster_index" field
        if "monster_index" not in data:
            raise ValidationError({"monster_index": "The key 'monster_index' is required."})
        # HINT: Validate monster_index is not empty and not too long
        # HINT: Raise ValidationError with proper field-specific messages
        monster_index = data.get("monster_index", "").strip()
        if not monster_index:
            raise ValidationError("The 'monster_index' field cannot be empty.")
        if len(monster_index) > 100:
            raise ValidationError("The 'monster_index' field must not exceed 100 characters.")      
        
        return data  # This passes validation!


class TestMonsterModel:
    """Unit tests for Monster model."""

    def test_create_monster_success(self, db_session):
        """
        🎯 TASK: Make this test pass by creating proper database fixtures

        WHAT THIS TEST DOES:
        - Creates a Monster object
        - Adds it to database session
        - Commits the transaction
        - Checks all fields were saved correctly

        WHAT YOU NEED TO FIX:
        - Set up proper SQLAlchemy database in conftest.py
        - Create Monster table with correct columns
        - Ensure db_session fixture works with in-memory database

        HINT: Check Step 7-8 in STUDENT_WORKSHOP_GUIDE.md
        """
        monster_data = {
            "index": "dragon",
            "name": "Ancient Red Dragon",
            "type": "dragon",
            "challenge_rating": 24
        }

        monster = Monster(
            index=monster_data["index"],
            name=monster_data["name"],
            data=monster_data
        )

        db_session.add(monster)
        db_session.commit()

        # Assertions
        assert monster.id is not None
        assert monster.index == "dragon"
        assert monster.name == "Ancient Red Dragon"
        assert monster.data["challenge_rating"] == 24
        assert monster.created_at is not None

    def test_monster_unique_constraint(self, db_session):
        """
        🎯 TASK: Make this test pass by ensuring Monster.index is unique

        WHAT THIS TEST DOES:
        - Creates two monsters with same index
        - Expects database to reject the duplicate

        WHAT YOU NEED TO FIX:
        - Monster model should have unique=True on index column
        - Database should raise IntegrityError on duplicate

        HINT: Check the Monster class definition above
        """
        # Create first monster
        monster1 = Monster(index="orc", name="Orc", data={})
        db_session.add(monster1)
        db_session.commit()

        # Try to create second monster with same index
        monster2 = Monster(index="orc", name="Another Orc", data={})
        db_session.add(monster2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_monster_required_fields(self):
        """
        🎯 TASK: Make this test pass by adding validation to Monster.__init__

        WHAT THIS TEST DOES:
        - Tries to create Monster without index or name
        - Expects ValueError with specific error messages

        WHAT YOU NEED TO FIX:
        - Go to Monster.__init__ method (line ~36)
        - Add validation: if index is None: raise ValueError("index is required")
        - Add validation: if name is None: raise ValueError("name is required")

        HINT: Replace the TODO comment in Monster.__init__ with proper validation. Done.
        """
        # Test missing index
        with pytest.raises(ValueError, match="index is required"):
            Monster(name="Test Monster", data={})

        # Test missing name
        with pytest.raises(ValueError, match="name is required"):
            Monster(index="test", data={})

    def test_monster_string_representation(self):
        """
        🎯 TASK: Make this test pass by fixing Monster.__str__ method

        WHAT THIS TEST DOES:
        - Creates a Monster object
        - Calls str(monster) and expects "Ancient Red Dragon (dragon)"

        WHAT YOU NEED TO FIX:
        - Go to Monster.__str__ method (line ~45)
        - Replace "Monster object" with f"{self.name} ({self.index})"

        HINT: Use f-string formatting to combine name and index
        """
        monster = Monster(
            index="dragon",
            name="Ancient Red Dragon",
            data={"type": "dragon"}
        )

        expected = "Ancient Red Dragon (dragon)"
        assert str(monster) == expected


class TestMonsterSchemas:
    """Unit tests for Marshmallow schemas."""

    def test_monster_list_request_schema_valid(self):
        """
        🎯 TASK: Fix MonsterListRequestSchema to validate properly

        WHAT THIS TEST DOES:
        - Calls schema.load({"resource": "monsters"})
        - Expects the data to be returned unchanged

        WHAT YOU NEED TO FIX:
        - Go to MonsterListRequestSchema.load() method (line ~53)
        - Add validation: check if "resource" field exists
        - Add validation: check if resource equals "monsters"
        - Return data if valid, raise ValidationError if not

        HINT: Replace the TODO comments with proper validation logic. Done.
        """
        schema = MonsterListRequestSchema()
        data = {"resource": "monsters"}

        result = schema.load(data)
        assert result["resource"] == "monsters"

    def test_monster_list_request_schema_invalid_resource(self):
        """
        🎯 TASK: Make this test pass by implementing schema validation errors

        WHAT THIS TEST DOES:
        - Tries to validate invalid resource type
        - Expects ValidationError with specific message

        WHAT YOU NEED TO FIX:
        - Schema should raise ValidationError for invalid resource
        - Error message should contain "Must be one of: monsters"

        HINT: Use marshmallow.ValidationError with proper format
        """
        from marshmallow import ValidationError

        schema = MonsterListRequestSchema()
        invalid_data = {"resource": "invalid_resource"}

        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)

        assert "Must be one of: monsters" in str(exc_info.value.messages)

    def test_monster_get_request_schema_valid(self):
        """
        🎯 TASK: Make this test pass by implementing monster get schema

        WHAT THIS TEST DOES:
        - Validates monster get request with valid index
        - Expects data to pass through unchanged

        WHAT YOU NEED TO FIX:
        - Schema should accept {"monster_index": "dragon"}
        - Validate monster_index is present and valid

        HINT: Check MonsterGetRequestSchema.load() method above
        """
        schema = MonsterGetRequestSchema()
        data = {"monster_index": "dragon"}

        result = schema.load(data)
        assert result["monster_index"] == "dragon"

    def test_monster_get_request_schema_missing_index(self):
        """
        🎯 TASK: Make this test pass by validating required fields

        WHAT THIS TEST DOES:
        - Tries to validate request without monster_index
        - Expects ValidationError mentioning monster_index

        WHAT YOU NEED TO FIX:
        - Schema should check for required monster_index field
        - Raise ValidationError with proper field name

        HINT: Error messages should be in dict format
        """
        from marshmallow import ValidationError

        schema = MonsterGetRequestSchema()

        with pytest.raises(ValidationError) as exc_info:
            schema.load({})

        assert "monster_index" in exc_info.value.messages

    @pytest.mark.parametrize("invalid_index", [
        "",  # Empty string
        "   ",  # Whitespace only
        "a" * 101,  # Too long
    ])
    def test_monster_get_request_schema_invalid_index(self, invalid_index):
        """
        🎯 TASK: Make this test pass by validating monster_index format

        WHAT THIS TEST DOES:
        - Tests various invalid monster_index values
        - Expects ValidationError for each invalid case

        WHAT YOU NEED TO FIX:
        - Schema should validate monster_index is not empty
        - Schema should validate monster_index length <= 100
        - Raise ValidationError for invalid values

        HINT: Check string length and strip whitespace
        """
        from marshmallow import ValidationError

        schema = MonsterGetRequestSchema()
        data = {"monster_index": invalid_index}

        with pytest.raises(ValidationError):
            schema.load(data)


class TestMonsterAPI:
    """Integration tests for Monster API endpoints."""

    def test_monsters_list_from_cache(self, client, db_session, sample_monster_data):
        """
        🎯 TASK: Make this test pass by creating Flask API endpoints

        WHAT THIS TEST DOES:
        - Adds a monster to the database
        - Makes POST request to /monsters endpoint
        - Expects JSON response with monster data

        WHAT YOU NEED TO FIX:
        - Create Flask app fixture in conftest.py
        - Add POST /monsters route that queries database
        - Share database session between test and Flask app
        - Return proper JSON response format

        HINT: Check Step 11 in STUDENT_WORKSHOP_GUIDE.md
        """
        # Setup - add monster to database
        monster = Monster(
            index=sample_monster_data["index"],
            name=sample_monster_data["name"],
            data=sample_monster_data
        )
        db_session.add(monster)
        db_session.commit()

        # Test
        response = client.post('/monsters',
                              data=json.dumps({"resource": "monsters"}),
                              content_type='application/json')

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == sample_monster_data["name"]
        assert data["results"][0]["index"] == sample_monster_data["index"]

    def test_monsters_list_from_external_api(self, client, monkeypatch):
        """
        🎯 TASK: Make this test pass by handling empty database

        WHAT THIS TEST DOES:
        - Mocks external API response
        - Makes request when no cached data exists
        - Expects fallback to external API or mock data

        WHAT YOU NEED TO FIX:
        - Flask route should handle case when database is empty
        - Return fallback mock data when no cached monsters
        - Mock requests.get for predictable testing

        HINT: Add fallback response in your Flask route
        """
        # Mock external API response
        mock_external_response = {
            "count": 2,
            "results": [
                {"index": "dragon", "name": "Dragon", "url": "/api/monsters/dragon"},
                {"index": "orc", "name": "Orc", "url": "/api/monsters/orc"}
            ]
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_external_response
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200

        monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock_response)

        # Test
        response = client.post('/monsters',
                              data=json.dumps({"resource": "monsters"}),
                              content_type='application/json')

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 2
        assert len(data["results"]) == 2
        assert data["results"][0]["name"] == "Dragon"
        assert data["results"][1]["name"] == "Orc"

    def test_monster_get_from_cache(self, client, db_session, sample_monster_data):
        """
        🎯 TASK: Make this test pass by creating monster get endpoint

        WHAT THIS TEST DOES:
        - Adds monster to database
        - Makes POST request to /monster endpoint
        - Expects specific monster data in response

        WHAT YOU NEED TO FIX:
        - Add POST /monster route in Flask app
        - Route should query database by monster_index
        - Return monster data including name, index, and data fields

        HINT: Check Step 11 in STUDENT_WORKSHOP_GUIDE.md
        """
        # Setup - add monster to database
        monster = Monster(
            index=sample_monster_data["index"],
            name=sample_monster_data["name"],
            data=sample_monster_data
        )
        db_session.add(monster)
        db_session.commit()

        # Test
        response = client.post('/monster',
                              data=json.dumps({"monster_index": sample_monster_data["index"]}),
                              content_type='application/json')

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == sample_monster_data["name"]
        assert data["index"] == sample_monster_data["index"]
        assert data["challenge_rating"] == sample_monster_data["challenge_rating"]