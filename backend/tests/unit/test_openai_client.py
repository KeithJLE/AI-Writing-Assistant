"""
Unit tests for app.llm.openai_client module.

This module will test the OpenAI client functionality,
including API communication, streaming, error handling, and configuration.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock

from app.llm.openai_client import OpenAIClient


class TestOpenAIClient:
    """Test class for OpenAI client."""

    @patch("app.llm.openai_client.OpenAI")
    @patch("app.llm.openai_client.SecureLLMPipeline")
    def test_openai_client_initialization(self, mock_pipeline, mock_openai):
        """Test OpenAI client initialization."""
        mock_openai.return_value = MagicMock()
        mock_pipeline.return_value = MagicMock()

        client = OpenAIClient()

        assert client.client is not None
        assert client.active_streams == {}
        assert client.security_pipeline is not None

    @patch("app.llm.openai_client.OpenAI")
    @patch("app.llm.openai_client.SecureLLMPipeline")
    def test_create_completion_stream_security_block(
        self, mock_pipeline, mock_openai
    ):
        """Test that security pipeline blocks malicious input."""
        mock_openai.return_value = MagicMock()
        mock_security = MagicMock()
        mock_security.input_filter.detect_injection.return_value = True
        mock_pipeline.return_value = mock_security

        client = OpenAIClient()

        with pytest.raises(
            ValueError, match="Input blocked due to security concerns"
        ):
            list(client.create_completion_stream("test-id", "malicious prompt"))

    @patch("app.llm.openai_client.OpenAI")
    @patch("app.llm.openai_client.SecureLLMPipeline")
    def test_create_completion_stream_success(self, mock_pipeline, mock_openai):
        """Test successful completion stream creation."""
        # Mock OpenAI client
        mock_openai_instance = MagicMock()
        mock_stream = MagicMock()
        mock_stream.__iter__ = Mock(return_value=iter(["Hello", " world"]))
        mock_openai_instance.responses.create.return_value = mock_stream
        mock_openai.return_value = mock_openai_instance

        # Mock security pipeline
        mock_security = MagicMock()
        mock_security.input_filter.detect_injection.return_value = False
        mock_security.input_filter.sanitize_input.return_value = "clean prompt"
        mock_security.output_validator.validate_output.return_value = True
        mock_pipeline.return_value = mock_security

        client = OpenAIClient()

        # Test stream creation
        stream = client.create_completion_stream("test-id", "test prompt")
        chunks = list(stream)

        assert len(chunks) == 2
        assert chunks == ["Hello", " world"]
        mock_security.input_filter.detect_injection.assert_called_once_with(
            "test prompt"
        )
        mock_security.input_filter.sanitize_input.assert_called_once_with(
            "test prompt"
        )
        mock_openai_instance.responses.create.assert_called_once()
