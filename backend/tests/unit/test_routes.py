"""
Unit tests for app.routes.rephrase module.

This module will test FastAPI route handlers,
including request handling, response formatting, and error cases.
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.routes.rephrase import router


class TestRephraseRoutes:
    """Test class for rephrase routes."""

    def setup_method(self):
        """Set up test client."""
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)

    @patch("app.routes.rephrase.rephrase_service")
    def test_create_rephrase_success(self, mock_service):
        """Test successful rephrase request creation."""
        mock_service.create_request.return_value = "test-request-id"

        response = self.client.post(
            "/v1/rephrase",
            json={"text": "Hello world", "styles": ["formal", "casual"]},
        )

        assert response.status_code == 200
        assert response.json() == {"request_id": "test-request-id"}
        mock_service.create_request.assert_called_once_with(
            "Hello world", ["formal", "casual"]
        )

    def test_create_rephrase_empty_text_allowed(self):
        """Test rephrase request with empty text - should be allowed by Pydantic."""
        response = self.client.post(
            "/v1/rephrase",
            json={"text": "", "styles": ["formal"]},  # Empty text is allowed
        )

        assert response.status_code == 200  # Should succeed

    def test_create_rephrase_missing_fields(self):
        """Test rephrase request with missing fields."""
        response = self.client.post(
            "/v1/rephrase",
            json={
                "text": "Hello world"
                # Missing styles field
            },
        )

        assert response.status_code == 422  # Validation error

    @patch("app.routes.rephrase.rephrase_service")
    def test_stream_rephrase_success(self, mock_service):
        """Test successful streaming rephrase."""
        mock_service.stream_rephrase.return_value = iter(
            ["data: chunk1\n\n", "data: chunk2\n\n"]
        )

        response = self.client.get("/v1/rephrase/stream?request_id=test-123")

        assert response.status_code == 200
        assert (
            response.headers["content-type"]
            == "text/event-stream; charset=utf-8"
        )

    def test_stream_rephrase_missing_request_id(self):
        """Test streaming rephrase without request_id."""
        response = self.client.get("/v1/rephrase/stream")

        assert (
            response.status_code == 422
        )  # FastAPI returns 422 for missing query params
