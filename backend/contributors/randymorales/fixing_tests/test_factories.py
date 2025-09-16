"""
Test data and mock factories.
This module provides factory classes for creating consistent test data and API mocks.
"""

import uuid
from unittest.mock import Mock
import requests
from test_config import TestConfig


class TestDataFactory:
    """Factory for creating test data with variations."""

    @staticmethod
    def create_monster_data(name="Godzilla", size="Gigantic", **overrides):
        """Create monster data with optional overrides."""
        base_data = {
            "name": name,
            "size": size,
            "description": f"A {size.lower()} monster named {name}",
            "power_level": 1000,
            "element": "Fire",
            "index": f"monster-{str(uuid.uuid4())[:8]}",
            "challenge_rating": 5,
            "type": "beast",
            "hit_points": 50,
            "armor_class": 15
        }
        base_data.update(overrides)
        return base_data

    @staticmethod
    def create_external_api_response(monster_name="APIMonster", **overrides):
        """Create external API response data."""
        base_response = {
            "data": {
                "monster": {
                    "name": monster_name,
                    "origin": "External API",
                    "verified": True
                }
            },
            "status": "success"
        }
        if overrides:
            base_response["data"]["monster"].update(overrides)
        return base_response

    @staticmethod
    def create_monster_variations():
        """Create multiple monster variations for comprehensive testing."""
        return [
            TestDataFactory.create_monster_data("Godzilla", "Gigantic"),
            TestDataFactory.create_monster_data("Pikachu", "Small", power_level=100, element="Electric"),
            TestDataFactory.create_monster_data("Smaug", "Large", power_level=2000, element="Fire"),
            TestDataFactory.create_monster_data("Cthulhu", "Colossal", power_level=9999, element="Cosmic")
        ]


class MockAPIResponseFactory:
    """Factory for creating consistent API mock responses."""

    @staticmethod
    def create_success_response(data, status_code=None):
        """Create a successful mock response."""
        status_code = status_code or TestConfig.HTTP_OK
        mock_response = Mock()
        mock_response.json.return_value = data
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = status_code
        return mock_response

    @staticmethod
    def create_error_response(status_code, exception_class=None, message=""):
        """Create an error mock response."""
        mock_response = Mock()
        mock_response.status_code = status_code

        if exception_class:
            mock_response.raise_for_status.side_effect = exception_class(message)

        return mock_response

    @staticmethod
    def create_exception_mock(exception_class, message=""):
        """Create a mock that raises an exception."""
        def mock_request(*args, **kwargs):
            raise exception_class(message)
        return mock_request

    @staticmethod
    def create_connection_error_mock(message="Failed to connect to external API"):
        """Create a connection error mock."""
        return MockAPIResponseFactory.create_exception_mock(requests.ConnectionError, message)

    @staticmethod
    def create_timeout_mock(message="Request timed out"):
        """Create a timeout error mock."""
        return MockAPIResponseFactory.create_exception_mock(requests.Timeout, message)

    @staticmethod
    def create_404_response():
        """Create a 404 Not Found response."""
        return MockAPIResponseFactory.create_error_response(
            TestConfig.HTTP_NOT_FOUND,
            requests.HTTPError,
            "404 Not Found"
        )
