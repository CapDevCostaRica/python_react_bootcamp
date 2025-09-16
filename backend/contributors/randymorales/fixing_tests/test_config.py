"""
Test configuration constants and settings.
This module contains all configuration constants used across the test suite.
"""


class TestConfig:
    """Test configuration constants."""

    # Cache and Performance Settings
    CACHE_TTL = 300  # 5 minutes cache for tests
    PERFORMANCE_THRESHOLD = 1.0  # seconds

    # Logging Configuration
    LOG_LEVEL = "WARNING"

    # HTTP Status Codes
    HTTP_OK = 200
    HTTP_NOT_FOUND = 404
    HTTP_BAD_REQUEST = 400
    HTTP_INTERNAL_ERROR = 500

    # Test Environment Settings
    TESTING_ENV = "true"

    # Database Configuration
    TEST_DATABASE_URL = "sqlite:///:memory:"

    # Flask Configuration
    FLASK_TESTING = True
    FLASK_WTF_CSRF_ENABLED = False
    FLASK_SECRET_KEY = "test-secret-key"
