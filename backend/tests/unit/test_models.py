"""
Unit tests for app.models.requests module.

This module will test Pydantic model validation,
including field validation, serialization, and error handling.
"""

import pytest
from pydantic import ValidationError

from app.models.requests import RephraseRequest, RephraseResponse


class TestRephraseRequest:
    """Test class for RephraseRequest model."""

    def test_valid_rephrase_request(self):
        """Test creation of valid RephraseRequest."""
        request = RephraseRequest(
            text="Hello world", styles=["formal", "casual"]
        )
        assert request.text == "Hello world"
        assert request.styles == ["formal", "casual"]

    def test_empty_text_validation(self):
        """Test validation with empty text - Pydantic allows empty strings by default."""
        # Pydantic allows empty strings, so this should pass
        request = RephraseRequest(text="", styles=["formal"])
        assert request.text == ""
        assert request.styles == ["formal"]

    def test_missing_text_validation(self):
        """Test validation with missing text field."""
        with pytest.raises(ValidationError):
            RephraseRequest(styles=["formal"])

    def test_missing_styles_validation(self):
        """Test validation with missing styles field."""
        with pytest.raises(ValidationError):
            RephraseRequest(text="Hello world")

    def test_empty_styles_list(self):
        """Test validation with empty styles list."""
        request = RephraseRequest(text="Hello world", styles=[])
        assert request.styles == []

    def test_invalid_styles_type(self):
        """Test validation with invalid styles type."""
        with pytest.raises(ValidationError):
            RephraseRequest(text="Hello world", styles="not a list")


class TestRephraseResponse:
    """Test class for RephraseResponse model."""

    def test_valid_rephrase_response(self):
        """Test creation of valid RephraseResponse."""
        response = RephraseResponse(request_id="test-123")
        assert response.request_id == "test-123"

    def test_missing_request_id_validation(self):
        """Test validation with missing request_id."""
        with pytest.raises(ValidationError):
            RephraseResponse()
