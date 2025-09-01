"""Unit tests for configuration management."""

import pytest
import os
from unittest.mock import patch

from tga_scoring_audit.config import Config


class TestConfig:
    """Test configuration management."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = Config()
        assert config.api_key is None
        assert config.base_url == "https://www.golfgenius.com/api_v2"
        assert config.request_timeout == 30
        assert config.max_retries == 3

    def test_set_api_key_valid(self) -> None:
        """Test setting valid API key."""
        config = Config()
        config.set_api_key("test_api_key_123")
        assert config.api_key == "test_api_key_123"

    def test_set_api_key_strips_whitespace(self) -> None:
        """Test API key whitespace stripping."""
        config = Config()
        config.set_api_key("  test_key  ")
        assert config.api_key == "test_key"

    def test_set_api_key_empty_raises_error(self) -> None:
        """Test empty API key raises error."""
        config = Config()
        with pytest.raises(ValueError, match="API key cannot be empty"):
            config.set_api_key("")

    def test_set_api_key_whitespace_only_raises_error(self) -> None:
        """Test whitespace-only API key raises error."""
        config = Config()
        with pytest.raises(ValueError, match="API key cannot be empty"):
            config.set_api_key("   ")

    def test_get_api_key_when_set(self) -> None:
        """Test getting API key when already set."""
        config = Config()
        config.set_api_key("test_key")
        assert config.get_api_key() == "test_key"

    def test_get_api_key_not_set_raises_error(self) -> None:
        """Test getting API key when not set raises error."""
        config = Config()
        with pytest.raises(ValueError, match="API key not set"):
            config.get_api_key()

    @patch.dict(os.environ, {"GOLF_GENIUS_API_KEY": "env_test_key"})
    def test_get_api_key_from_environment(self) -> None:
        """Test getting API key from environment variable."""
        config = Config()
        assert config.get_api_key() == "env_test_key"

    def test_validate_api_key_valid(self) -> None:
        """Test API key validation with valid key."""
        config = Config()
        assert config.validate_api_key("test_api_key_123") is True

    def test_validate_api_key_too_short(self) -> None:
        """Test API key validation with short key."""
        config = Config()
        assert config.validate_api_key("short") is False

    def test_validate_api_key_empty(self) -> None:
        """Test API key validation with empty key."""
        config = Config()
        assert config.validate_api_key("") is False
