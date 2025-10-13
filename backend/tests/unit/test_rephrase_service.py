"""
Unit tests for app.services.rephrase module.

This module will test the RephraseService class and related functionality,
including request creation, streaming, cancellation, and error handling.
"""

import pytest
import uuid
import json
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.rephrase import (
    RephraseService,
    active_requests,
    cancel_request,
)
from app.security.output_validator import OutputValidator


class MockEvent:
    """Mock event object for testing streaming."""

    def __init__(self, event_type: str, delta: str = ""):
        self.type = event_type
        self.delta = delta


class TestRephraseService:
    """Test cases for RephraseService class."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        # Clear active requests before each test
        active_requests.clear()

        # Create service instance
        self.service = RephraseService()

        # Mock dependencies
        self.mock_output_validator = MagicMock(spec=OutputValidator)
        self.mock_output_validator.validate_output.return_value = True
        self.service.output_validator = self.mock_output_validator

    def test_create_request(self):
        """Test creating a new rephrase request."""
        text = "Hello world"
        styles = ["professional", "casual"]

        request_id = self.service.create_request(text, styles)

        # Verify request_id is a valid UUID
        assert uuid.UUID(request_id) is not None

        # Verify request is stored in active_requests
        assert request_id in active_requests
        assert active_requests[request_id]["text"] == text
        assert active_requests[request_id]["styles"] == styles
        assert active_requests[request_id]["status"] == "created"

    def test_create_request_unique_ids(self):
        """Test that create_request generates unique request IDs."""
        text = "Test text"
        styles = ["professional"]

        request_id_1 = self.service.create_request(text, styles)
        request_id_2 = self.service.create_request(text, styles)

        assert request_id_1 != request_id_2
        assert len(active_requests) == 2

    @pytest.mark.asyncio
    async def test_stream_rephrase_request_not_found(self):
        """Test streaming with non-existent request ID."""
        mock_request = AsyncMock()
        invalid_request_id = "non-existent-id"

        # Collect stream results
        results = []
        async for event in self.service.stream_rephrase(
            mock_request, invalid_request_id
        ):
            results.append(event)

        # Verify error response
        assert len(results) == 1
        event_data = json.loads(results[0].replace("data: ", "").strip())
        assert event_data["type"] == "error"
        assert event_data["message"] == "Request not found"

    @pytest.mark.asyncio
    @patch("app.services.rephrase.openai_client")
    async def test_stream_rephrase_success(self, mock_openai_client):
        """Test successful streaming of rephrase results."""
        # Setup
        text = "Hello world"
        styles = ["professional"]
        request_id = self.service.create_request(text, styles)

        # Mock FastAPI request
        mock_request = AsyncMock()
        mock_request.is_disconnected.return_value = False

        # Mock OpenAI streaming response
        mock_events = [
            MockEvent("response.output_text.delta", "Hello"),
            MockEvent("response.output_text.delta", " everyone"),
        ]
        mock_openai_client.create_completion_stream.return_value = mock_events

        # Collect stream results
        results = []
        async for event in self.service.stream_rephrase(
            mock_request, request_id
        ):
            results.append(event)

        # Verify OpenAI client was called correctly
        mock_openai_client.create_completion_stream.assert_called_once_with(
            request_id=request_id, prompt=text, style="professional"
        )

        # Verify output validation was called
        assert self.mock_output_validator.validate_output.call_count == 2

        # Parse and verify events
        assert len(results) == 4  # 2 delta events + 1 complete + 1 end

        # Check delta events
        delta_1 = json.loads(results[0].replace("data: ", "").strip())
        assert delta_1["type"] == "delta"
        assert delta_1["style"] == "professional"
        assert delta_1["text"] == "Hello"

        delta_2 = json.loads(results[1].replace("data: ", "").strip())
        assert delta_2["type"] == "delta"
        assert delta_2["style"] == "professional"
        assert delta_2["text"] == " everyone"

        # Check complete event
        complete_event = json.loads(results[2].replace("data: ", "").strip())
        assert complete_event["type"] == "complete"
        assert complete_event["style"] == "professional"

        # Check end event
        end_event = json.loads(results[3].replace("data: ", "").strip())
        assert end_event["type"] == "end"

    @pytest.mark.asyncio
    @patch("app.services.rephrase.openai_client")
    async def test_stream_rephrase_client_disconnect(self, mock_openai_client):
        """Test streaming when client disconnects."""
        # Setup
        text = "Hello world"
        styles = ["professional"]
        request_id = self.service.create_request(text, styles)

        # Mock FastAPI request - client disconnects after first event
        mock_request = AsyncMock()
        mock_request.is_disconnected.side_effect = [False, True]

        # Mock OpenAI streaming response
        mock_events = [
            MockEvent("response.output_text.delta", "Hello"),
            MockEvent("response.output_text.delta", " everyone"),
        ]
        mock_openai_client.create_completion_stream.return_value = mock_events

        # Collect stream results
        results = []
        async for event in self.service.stream_rephrase(
            mock_request, request_id
        ):
            results.append(event)

        # Verify stream was closed
        assert mock_openai_client.close_stream.call_count == 2
        mock_openai_client.close_stream.assert_called_with(request_id)

        # Should only get one delta event before disconnection
        assert len(results) == 1
        delta_event = json.loads(results[0].replace("data: ", "").strip())
        assert delta_event["type"] == "delta"
        assert delta_event["text"] == "Hello"

    @pytest.mark.asyncio
    @patch("app.services.rephrase.openai_client")
    async def test_stream_rephrase_security_validation_failure(
        self, mock_openai_client
    ):
        """Test streaming when output validation fails."""
        # Setup
        text = "Hello world"
        styles = ["professional"]
        request_id = self.service.create_request(text, styles)

        # Mock FastAPI request
        mock_request = AsyncMock()
        mock_request.is_disconnected.return_value = False

        # Mock output validator to reject content
        self.mock_output_validator.validate_output.return_value = False

        # Mock OpenAI streaming response
        mock_events = [
            MockEvent("response.output_text.delta", "Suspicious content"),
        ]
        mock_openai_client.create_completion_stream.return_value = mock_events

        # Collect stream results
        results = []
        async for event in self.service.stream_rephrase(
            mock_request, request_id
        ):
            results.append(event)

        # Verify security error was sent
        assert len(results) == 3  # error + complete + end

        error_event = json.loads(results[0].replace("data: ", "").strip())
        assert error_event["type"] == "error"
        assert error_event["style"] == "professional"
        assert "security concerns" in error_event["text"]

    @pytest.mark.asyncio
    @patch("app.services.rephrase.openai_client")
    async def test_stream_rephrase_multiple_styles(self, mock_openai_client):
        """Test streaming with multiple styles."""
        # Setup
        text = "Hello world"
        styles = ["professional", "casual"]
        request_id = self.service.create_request(text, styles)

        # Mock FastAPI request
        mock_request = AsyncMock()
        mock_request.is_disconnected.return_value = False

        # Mock OpenAI streaming response - return different events for each style
        mock_openai_client.create_completion_stream.side_effect = [
            [MockEvent("response.output_text.delta", "Good morning")],
            [MockEvent("response.output_text.delta", "Hey there")],
        ]

        # Collect stream results
        results = []
        async for event in self.service.stream_rephrase(
            mock_request, request_id
        ):
            results.append(event)

        # Verify OpenAI client was called for each style
        assert mock_openai_client.create_completion_stream.call_count == 2

        # Verify we got events for both styles
        assert len(results) == 5  # 2 delta + 2 complete + 1 end

        # Parse events
        events = [
            json.loads(result.replace("data: ", "").strip())
            for result in results
        ]

        # Check professional style
        assert events[0]["type"] == "delta"
        assert events[0]["style"] == "professional"
        assert events[0]["text"] == "Good morning"

        assert events[1]["type"] == "complete"
        assert events[1]["style"] == "professional"

        # Check casual style
        assert events[2]["type"] == "delta"
        assert events[2]["style"] == "casual"
        assert events[2]["text"] == "Hey there"

        assert events[3]["type"] == "complete"
        assert events[3]["style"] == "casual"

        # Check end event
        assert events[4]["type"] == "end"

    @pytest.mark.asyncio
    @patch("app.services.rephrase.openai_client")
    async def test_stream_rephrase_exception_handling(self, mock_openai_client):
        """Test streaming with exception handling."""
        # Setup
        text = "Hello world"
        styles = ["professional"]
        request_id = self.service.create_request(text, styles)

        # Mock FastAPI request
        mock_request = AsyncMock()
        mock_request.is_disconnected.return_value = False

        # Mock OpenAI client to raise exception
        mock_openai_client.create_completion_stream.side_effect = Exception(
            "API Error"
        )

        # Collect stream results
        results = []
        async for event in self.service.stream_rephrase(
            mock_request, request_id
        ):
            results.append(event)

        # Verify error event was sent
        assert len(results) == 1
        error_event = json.loads(results[0].replace("data: ", "").strip())
        assert error_event["type"] == "error"
        assert "API Error" in error_event["message"]

        # Verify cleanup was called
        mock_openai_client.close_stream.assert_called_once_with(request_id)


class TestCancelRequest:
    """Test cases for cancel_request function."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        active_requests.clear()

    @patch("app.services.rephrase.openai_client")
    def test_cancel_request_success(self, mock_openai_client):
        """Test successfully canceling an active request."""
        # Create an active request
        request_id = str(uuid.uuid4())
        active_requests[request_id] = {
            "text": "Hello",
            "styles": ["professional"],
            "status": "processing",
        }

        # Mock successful stream close
        mock_openai_client.close_stream.return_value = True

        # Cancel the request
        result = cancel_request(request_id)

        # Verify cancellation
        assert result is True
        assert request_id not in active_requests
        mock_openai_client.close_stream.assert_called_once_with(request_id)

    @patch("app.services.rephrase.openai_client")
    def test_cancel_request_not_found(self, mock_openai_client):
        """Test canceling a non-existent request."""
        non_existent_id = "non-existent-id"

        # Cancel the request
        result = cancel_request(non_existent_id)

        # Verify no cancellation occurred
        assert result is False
        mock_openai_client.close_stream.assert_not_called()

    @patch("app.services.rephrase.openai_client")
    def test_cancel_request_stream_close_fails(self, mock_openai_client):
        """Test canceling request when stream close fails."""
        # Create an active request
        request_id = str(uuid.uuid4())
        active_requests[request_id] = {
            "text": "Hello",
            "styles": ["professional"],
            "status": "processing",
        }

        # Mock failed stream close
        mock_openai_client.close_stream.return_value = False

        # Cancel the request
        result = cancel_request(request_id)

        # Verify request was still removed even if stream close failed
        assert result is False
        assert request_id not in active_requests
        mock_openai_client.close_stream.assert_called_once_with(request_id)
