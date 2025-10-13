"""
Unit tests for app.config module.

This module will test the configuration management functionality,
including environment variable loading, validation, and default values.
"""

import pytest
from unittest.mock import patch

# Don't import Settings class directly to avoid early evaluation
import app.config


class TestSettings:
    """Test class for Settings configuration."""

    @patch("os.getenv")
    def test_settings_with_api_key(self, mock_getenv):
        """Test Settings initialization with API key."""

        def mock_getenv_side_effect(key, default=None):
            if key == "OPENAI_API_KEY":
                return "test-api-key"
            elif key == "SERVE_FRONTEND":
                return "false"
            elif key == "FRONTEND_DIR":
                return default
            return default

        mock_getenv.side_effect = mock_getenv_side_effect

        # Reload the module to get fresh Settings class
        import importlib

        importlib.reload(app.config)

        settings = app.config.Settings()
        assert settings.OPENAI_API_KEY == "test-api-key"
        assert settings.APP_NAME == "AI Writing Assistant"
        assert settings.SERVE_FRONTEND is False

    @patch("os.getenv")
    def test_settings_without_api_key(self, mock_getenv):
        """Test Settings initialization without API key."""

        def mock_getenv_side_effect(key, default=None):
            if key == "OPENAI_API_KEY":
                return None
            elif key == "SERVE_FRONTEND":
                return "false"
            elif key == "FRONTEND_DIR":
                return default
            return default

        mock_getenv.side_effect = mock_getenv_side_effect

        # Reload the module to get fresh Settings class
        import importlib

        importlib.reload(app.config)

        settings = app.config.Settings()
        assert settings.OPENAI_API_KEY is None

    @patch("os.getenv")
    def test_serve_frontend_true(self, mock_getenv):
        """Test SERVE_FRONTEND setting with true value."""

        def mock_getenv_side_effect(key, default=None):
            if key == "OPENAI_API_KEY":
                return "test-key"
            elif key == "SERVE_FRONTEND":
                return "true"
            elif key == "FRONTEND_DIR":
                return default
            return default

        mock_getenv.side_effect = mock_getenv_side_effect

        # Reload the module to get fresh Settings class
        import importlib

        importlib.reload(app.config)

        settings = app.config.Settings()
        assert settings.SERVE_FRONTEND is True

    @patch("os.getenv")
    def test_validate_success(self, mock_getenv):
        """Test successful validation with API key."""

        def mock_getenv_side_effect(key, default=None):
            if key == "OPENAI_API_KEY":
                return "test-key"
            elif key == "SERVE_FRONTEND":
                return "false"
            elif key == "FRONTEND_DIR":
                return default
            return default

        mock_getenv.side_effect = mock_getenv_side_effect

        # Reload the module to get fresh Settings class
        import importlib

        importlib.reload(app.config)

        settings = app.config.Settings()
        # Should not raise an exception
        settings.validate()

    @patch("os.getenv")
    def test_validate_failure(self, mock_getenv):
        """Test validation failure without API key."""

        def mock_getenv_side_effect(key, default=None):
            if key == "OPENAI_API_KEY":
                return None
            elif key == "SERVE_FRONTEND":
                return "false"
            elif key == "FRONTEND_DIR":
                return default
            return default

        mock_getenv.side_effect = mock_getenv_side_effect

        # Reload the module to get fresh Settings class
        import importlib

        importlib.reload(app.config)

        settings = app.config.Settings()
        with pytest.raises(
            ValueError, match="OPENAI_API_KEY environment variable is required"
        ):
            settings.validate()
