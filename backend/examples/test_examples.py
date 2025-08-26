"""
Example implementation of comprehensive tests for D&D Monster Service
This demonstrates testing best practices discussed in the workshop.
"""

import pytest
import json
import time
import threading
from unittest.mock import Mock, patch
from sqlalchemy.exc import IntegrityError
import requests


class TestMonsterModel:
    """Unit tests for Monster model."""

    def test_create_monster_success(self, db_session):
        """Test successful monster creation."""
        from your_app.models import Monster

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
        """Test that monster index must be unique."""
        from your_app.models import Monster

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
        """Test that required fields are validated."""
        from your_app.models import Monster

        # Test missing index
        with pytest.raises(ValueError, match="index is required"):
            Monster(name="Test Monster", data={})

        # Test missing name
        with pytest.raises(ValueError, match="name is required"):
            Monster(index="test", data={})

    def test_monster_string_representation(self):
        """Test string representation of monster."""
        from your_app.models import Monster

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
        """Test valid monster list request schema."""
        from your_app.schemas import MonsterListRequestSchema

        schema = MonsterListRequestSchema()
        data = {"resource": "monsters"}

        result = schema.load(data)
        assert result["resource"] == "monsters"

    def test_monster_list_request_schema_invalid_resource(self):
        """Test invalid resource in monster list request."""
        from your_app.schemas import MonsterListRequestSchema
        from marshmallow import ValidationError

        schema = MonsterListRequestSchema()
        invalid_data = {"resource": "invalid_resource"}

        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)

        assert "Must be one of: monsters" in str(exc_info.value.messages)

    def test_monster_get_request_schema_valid(self):
        """Test valid monster get request schema."""
        from your_app.schemas import MonsterGetRequestSchema

        schema = MonsterGetRequestSchema()
        data = {"monster_index": "dragon"}

        result = schema.load(data)
        assert result["monster_index"] == "dragon"

    def test_monster_get_request_schema_missing_index(self):
        """Test missing monster_index in get request."""
        from your_app.schemas import MonsterGetRequestSchema
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
        """Test various invalid monster indices."""
        from your_app.schemas import MonsterGetRequestSchema
        from marshmallow import ValidationError

        schema = MonsterGetRequestSchema()
        data = {"monster_index": invalid_index}

        with pytest.raises(ValidationError):
            schema.load(data)


class TestMonsterAPI:
    """Integration tests for Monster API endpoints."""

    def test_monsters_list_from_cache(self, client, db_session, sample_monster_data):
        """Test monsters list endpoint when data exists in cache."""
        from your_app.models import Monster

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
        """Test monsters list endpoint when fetching from external API."""
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
        """Test get monster endpoint when data exists in cache."""
        from your_app.models import Monster

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

    def test_monster_get_from_external_api_and_cache(self, client, db_session, monkeypatch):
        """Test get monster from external API and verify it gets cached."""
        from your_app.models import Monster

        # Mock external API response
        external_monster_data = {
            "index": "orc",
            "name": "Orc",
            "type": "humanoid",
            "challenge_rating": 0.5,
            "armor_class": 13,
            "hit_points": 15
        }

        mock_response = Mock()
        mock_response.json.return_value = external_monster_data
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200

        monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock_response)

        # Verify monster is not in cache initially
        cached_monster = db_session.query(Monster).filter_by(index="orc").first()
        assert cached_monster is None

        # Test
        response = client.post('/monster',
                              data=json.dumps({"monster_index": "orc"}),
                              content_type='application/json')

        # Assert response
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Orc"
        assert data["index"] == "orc"

        # Verify monster was cached in database
        cached_monster = db_session.query(Monster).filter_by(index="orc").first()
        assert cached_monster is not None
        assert cached_monster.name == "Orc"
        assert cached_monster.data["challenge_rating"] == 0.5

    @pytest.mark.parametrize("invalid_payload", [
        {},  # Empty payload
        {"wrong_key": "monsters"},  # Wrong key
        {"resource": "invalid"},  # Invalid resource
        {"resource": ""},  # Empty resource
    ])
    def test_monsters_list_invalid_payloads(self, client, invalid_payload):
        """Test monsters list endpoint with invalid payloads."""
        response = client.post('/monsters',
                              data=json.dumps(invalid_payload),
                              content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_malformed_json_request(self, client):
        """Test API with malformed JSON."""
        response = client.post('/monsters',
                              data='{"invalid": json}',
                              content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "json" in data["error"].lower()


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_external_api_timeout(self, client, monkeypatch):
        """Test handling of external API timeout."""
        def mock_timeout(*args, **kwargs):
            raise requests.Timeout("Request timed out")

        monkeypatch.setattr("requests.get", mock_timeout)

        response = client.post('/monster',
                              data=json.dumps({"monster_index": "dragon"}),
                              content_type='application/json')

        assert response.status_code == 503  # Service Unavailable
        data = response.get_json()
        assert "error" in data
        assert "timeout" in data["error"].lower()

    def test_external_api_connection_error(self, client, monkeypatch):
        """Test handling of external API connection error."""
        def mock_connection_error(*args, **kwargs):
            raise requests.ConnectionError("Connection failed")

        monkeypatch.setattr("requests.get", mock_connection_error)

        response = client.post('/monster',
                              data=json.dumps({"monster_index": "dragon"}),
                              content_type='application/json')

        assert response.status_code == 503
        data = response.get_json()
        assert "error" in data
        assert "external service" in data["error"].lower()

    def test_external_api_404_not_found(self, client, monkeypatch):
        """Test handling when monster not found in external API."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_response.status_code = 404

        monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock_response)

        response = client.post('/monster',
                              data=json.dumps({"monster_index": "nonexistent"}),
                              content_type='application/json')

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
        assert "not found" in data["error"].lower()

    def test_external_api_500_server_error(self, client, monkeypatch):
        """Test handling when external API returns server error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Internal Server Error")
        mock_response.status_code = 500

        monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock_response)

        response = client.post('/monster',
                              data=json.dumps({"monster_index": "dragon"}),
                              content_type='application/json')

        assert response.status_code == 503
        data = response.get_json()
        assert "error" in data

    def test_database_commit_failure(self, client, db_session, monkeypatch):
        """Test handling when database commit fails."""
        from sqlalchemy.exc import SQLAlchemyError

        # Mock successful external API
        mock_external_response = {
            "index": "troll",
            "name": "Troll",
            "type": "giant"
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_external_response
        mock_response.raise_for_status.return_value = None

        monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock_response)

        # Mock database commit failure
        original_commit = db_session.commit
        def mock_commit():
            raise SQLAlchemyError("Database connection lost")

        monkeypatch.setattr(db_session, "commit", mock_commit)

        response = client.post('/monster',
                              data=json.dumps({"monster_index": "troll"}),
                              content_type='application/json')

        # Should still return data from external API
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Troll"

        # But data should not be in cache due to commit failure
        # Restore original commit to check database state
        monkeypatch.setattr(db_session, "commit", original_commit)
        from your_app.models import Monster
        cached_monster = db_session.query(Monster).filter_by(index="troll").first()
        assert cached_monster is None


class TestPerformance:
    """Performance tests."""

    def test_api_response_time(self, client, db_session, sample_monster_data):
        """Test that API responds within acceptable time."""
        from your_app.models import Monster

        # Setup cached data for fast response
        monster = Monster(
            index=sample_monster_data["index"],
            name=sample_monster_data["name"],
            data=sample_monster_data
        )
        db_session.add(monster)
        db_session.commit()

        # Measure response time
        start_time = time.time()
        response = client.post('/monster',
                              data=json.dumps({"monster_index": sample_monster_data["index"]}),
                              content_type='application/json')
        end_time = time.time()

        response_time = end_time - start_time

        # Assertions
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second

    def test_concurrent_requests_cached_data(self, client, db_session, sample_monster_data):
        """Test handling of concurrent requests to cached data."""
        from your_app.models import Monster
        import queue

        # Setup cached data
        monster = Monster(
            index=sample_monster_data["index"],
            name=sample_monster_data["name"],
            data=sample_monster_data
        )
        db_session.add(monster)
        db_session.commit()

        results = queue.Queue()

        def make_request():
            response = client.post('/monster',
                                  data=json.dumps({"monster_index": sample_monster_data["index"]}),
                                  content_type='application/json')
            results.put((response.status_code, response.get_json()))

        # Create and start multiple threads
        threads = []
        num_threads = 10
        for _ in range(num_threads):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check all requests succeeded
        status_codes = []
        response_data = []
        while not results.empty():
            status, data = results.get()
            status_codes.append(status)
            response_data.append(data)

        assert len(status_codes) == num_threads
        assert all(code == 200 for code in status_codes)
        assert all(data["name"] == sample_monster_data["name"] for data in response_data)

    @pytest.mark.slow
    def test_large_number_of_monsters_in_cache(self, client, db_session):
        """Test performance with large number of monsters in cache."""
        from your_app.models import Monster

        # Create many monsters in cache
        monsters = []
        for i in range(1000):
            monster = Monster(
                index=f"monster_{i}",
                name=f"Monster {i}",
                data={"type": "test", "challenge_rating": i % 30}
            )
            monsters.append(monster)

        db_session.add_all(monsters)
        db_session.commit()

        # Test list endpoint performance
        start_time = time.time()
        response = client.post('/monsters',
                              data=json.dumps({"resource": "monsters"}),
                              content_type='application/json')
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 1000
        assert response_time < 5.0  # Should handle large dataset within 5 seconds


class TestCacheStrategy:
    """Test caching strategy and behavior."""

    def test_cache_hit_vs_cache_miss(self, client, db_session, monkeypatch):
        """Test difference between cache hit and cache miss."""
        from your_app.models import Monster

        # Mock external API (for cache miss)
        external_api_called = []

        def mock_external_api(*args, **kwargs):
            external_api_called.append(True)
            mock_response = Mock()
            mock_response.json.return_value = {
                "index": "dragon",
                "name": "Dragon",
                "type": "dragon"
            }
            mock_response.raise_for_status.return_value = None
            return mock_response

        monkeypatch.setattr("requests.get", mock_external_api)

        # First request - cache miss, should call external API
        response1 = client.post('/monster',
                               data=json.dumps({"monster_index": "dragon"}),
                               content_type='application/json')

        assert response1.status_code == 200
        assert len(external_api_called) == 1  # External API should be called

        # Verify data was cached
        cached_monster = db_session.query(Monster).filter_by(index="dragon").first()
        assert cached_monster is not None

        # Second request - cache hit, should NOT call external API
        response2 = client.post('/monster',
                               data=json.dumps({"monster_index": "dragon"}),
                               content_type='application/json')

        assert response2.status_code == 200
        assert len(external_api_called) == 1  # External API should NOT be called again

        # Responses should be identical
        assert response1.get_json() == response2.get_json()

    def test_cache_isolation_between_monsters(self, client, db_session, monkeypatch):
        """Test that caching one monster doesn't affect others."""
        from your_app.models import Monster

        # Add one monster to cache
        monster1 = Monster(
            index="dragon",
            name="Dragon",
            data={"type": "dragon", "challenge_rating": 24}
        )
        db_session.add(monster1)
        db_session.commit()

        # Mock external API for different monster
        mock_response = Mock()
        mock_response.json.return_value = {
            "index": "orc",
            "name": "Orc",
            "type": "humanoid",
            "challenge_rating": 0.5
        }
        mock_response.raise_for_status.return_value = None

        monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock_response)

        # Request cached monster - should not call external API
        with patch("requests.get") as mock_get:
            response1 = client.post('/monster',
                                   data=json.dumps({"monster_index": "dragon"}),
                                   content_type='application/json')
            mock_get.assert_not_called()

        # Request non-cached monster - should call external API
        response2 = client.post('/monster',
                               data=json.dumps({"monster_index": "orc"}),
                               content_type='application/json')

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.get_json()["name"] == "Dragon"
        assert response2.get_json()["name"] == "Orc"


# Additional helper functions for testing
def assert_valid_monster_response(response_data):
    """Custom assertion for monster response validation."""
    required_fields = ["index", "name"]

    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"

    assert isinstance(response_data["index"], str)
    assert len(response_data["index"]) > 0
    assert isinstance(response_data["name"], str)
    assert len(response_data["name"]) > 0


def assert_valid_monsters_list_response(response_data):
    """Custom assertion for monsters list response validation."""
    required_fields = ["count", "results"]

    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"

    assert isinstance(response_data["count"], int)
    assert response_data["count"] >= 0
    assert isinstance(response_data["results"], list)
    assert len(response_data["results"]) == response_data["count"]

    for monster in response_data["results"]:
        assert_valid_monster_response(monster)
