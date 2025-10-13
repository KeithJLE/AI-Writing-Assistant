"""
Integration tests for service and route layers.

Tests the integration between FastAPI routes, rephrase service,
and OpenAI client without external dependencies.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.routes.rephrase import router
from app.services.rephrase import RephraseService


class TestServiceRouteIntegration:
    """Test integration between routes and services."""

    def setup_method(self):
        """Set up test client."""
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)

    @patch("app.routes.rephrase.rephrase_service")
    def test_full_rephrase_workflow(self, mock_service):
        """Test complete rephrase workflow from request to response."""
        # Mock service methods
        mock_service.create_request.return_value = "test-request-123"
        mock_service.stream_rephrase.return_value = iter(
            ["data: chunk1\n\n", "data: chunk2\n\n", "data: [DONE]\n\n"]
        )

        # Step 1: Create rephrase request
        create_response = self.client.post(
            "/v1/rephrase",
            json={"text": "Hello world", "styles": ["formal", "casual"]},
        )

        assert create_response.status_code == 200
        request_data = create_response.json()
        assert request_data["request_id"] == "test-request-123"

        # Verify service was called correctly
        mock_service.create_request.assert_called_once_with(
            "Hello world", ["formal", "casual"]
        )

        # Step 2: Stream the results
        stream_response = self.client.get(
            f"/v1/rephrase/stream?request_id={request_data['request_id']}"
        )

        assert stream_response.status_code == 200
        assert (
            stream_response.headers["content-type"]
            == "text/event-stream; charset=utf-8"
        )

    @patch("app.routes.rephrase.rephrase_service")
    def test_error_handling_integration(self, mock_service):
        """Test error handling across route and service layers."""
        # Mock service to raise an exception
        mock_service.create_request.side_effect = ValueError("Invalid input")

        with pytest.raises(Exception):
            response = self.client.post(
                "/v1/rephrase", json={"text": "Test text", "styles": ["formal"]}
            )


class TestServiceDependencyIntegration:
    """Test service integration with its dependencies."""

    def setup_method(self):
        """Set up service instance."""
        self.service = RephraseService()

    def test_service_initialization(self):
        """Test that service initializes with required dependencies."""
        # Service should have required attributes
        assert hasattr(self.service, "output_validator")
        # The openai_client is imported as a module-level variable, not a class attribute

    @patch("app.services.rephrase.openai_client")
    def test_service_openai_integration(self, mock_openai_client):
        """Test service integration with OpenAI client."""
        # Mock OpenAI client
        mock_stream = MagicMock()
        mock_stream.__iter__ = MagicMock(
            return_value=iter(["chunk1", "chunk2", "chunk3"])
        )
        mock_openai_client.create_completion_stream.return_value = mock_stream

        # Create a request
        request_id = self.service.create_request("Test text", ["formal"])
        assert request_id is not None

        # Check the global active_requests dict
        from app.services.rephrase import active_requests

        assert request_id in active_requests

        # Verify request data
        request_data = active_requests[request_id]
        assert request_data["text"] == "Test text"
        assert request_data["styles"] == ["formal"]

    def test_request_id_generation(self):
        """Test that service generates unique request IDs."""
        request_id1 = self.service.create_request("Text 1", ["formal"])
        request_id2 = self.service.create_request("Text 2", ["casual"])

        assert request_id1 != request_id2
        assert len(request_id1) > 0
        assert len(request_id2) > 0

        # Check the global active_requests dict
        from app.services.rephrase import active_requests

        assert request_id1 in active_requests
        assert request_id2 in active_requests
