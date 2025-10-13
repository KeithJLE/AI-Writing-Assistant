"""Test configuration and common fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Generator


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Mock OpenAI client for testing."""
    mock_client = MagicMock()
    mock_stream = MagicMock()
    mock_client.responses.create.return_value = mock_stream
    return mock_client


@pytest.fixture
def mock_output_validator() -> MagicMock:
    """Mock output validator for testing."""
    mock_validator = MagicMock()
    mock_validator.validate_output.return_value = True
    return mock_validator


@pytest.fixture
def sample_rephrase_text() -> str:
    """Sample text for testing rephrase functionality."""
    return "Hey guys, let's huddle about AI."


@pytest.fixture
def sample_styles() -> list[str]:
    """Sample styles for testing."""
    return ["professional", "casual", "polite", "social"]
