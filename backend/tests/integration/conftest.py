"""
Pytest configuration for integration and e2e tests.

This file provides additional fixtures and configuration
specifically for integration and end-to-end testing.
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_openai_responses():
    """Mock OpenAI responses for consistent testing."""
    return {
        "formal": iter(
            [
                "Here is the text rephrased in a formal style: ",
                "Good morning, I hope this message finds you well.",
            ]
        ),
        "casual": iter(
            [
                "Here's the text in a casual style: ",
                "Hey there! Hope you're doing great!",
            ]
        ),
        "polite": iter(
            [
                "Here is a polite version: ",
                "Hello, I hope you are having a wonderful day.",
            ]
        ),
    }


@pytest.fixture
def mock_security_pipeline():
    """Mock security pipeline for integration tests."""
    with patch("app.security.secure_llm_pipeline.SecureLLMPipeline") as mock:
        mock_instance = MagicMock()
        mock_instance.input_filter.detect_injection.return_value = False
        mock_instance.input_filter.sanitize_input.side_effect = lambda x: x
        mock_instance.output_validator.validate_output.return_value = True
        mock_instance.output_validator.filter_response.side_effect = lambda x: x
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_requests():
    """Sample request data for testing."""
    return [
        {"text": "Hello, how are you?", "styles": ["formal"]},
        {"text": "Thanks for your help!", "styles": ["casual", "polite"]},
        {
            "text": "I need assistance with this project.",
            "styles": ["professional", "friendly"],
        },
    ]


pytest_markers = [
    "integration: marks tests as integration tests",
    "e2e: marks tests as end-to-end tests",
    "slow: marks tests as slow running",
]


def pytest_configure(config):
    """Configure pytest with custom markers."""
    for marker in pytest_markers:
        config.addinivalue_line("markers", marker)
