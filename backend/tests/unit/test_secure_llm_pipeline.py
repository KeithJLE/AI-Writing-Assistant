"""
Unit tests for app.security.secure_llm_pipeline module.

This module will test the secure LLM pipeline orchestration,
including security layer integration, pipeline flow, and error handling.
"""

from unittest.mock import patch, MagicMock

from app.security.secure_llm_pipeline import (
    SecureLLMPipeline,
    create_structured_prompt,
    generate_system_prompt,
)


class TestSecureLLMPipeline:
    """Test class for SecureLLMPipeline."""

    def setup_method(self):
        """Set up SecureLLMPipeline instance."""
        self.pipeline = SecureLLMPipeline()

    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        assert self.pipeline.input_filter is not None
        assert self.pipeline.output_validator is not None

    @patch("app.security.secure_llm_pipeline.PromptInjectionFilter")
    @patch("app.security.secure_llm_pipeline.OutputValidator")
    def test_pipeline_with_mocked_components(self, mock_validator, mock_filter):
        """Test pipeline with mocked security components."""
        mock_filter_instance = MagicMock()
        mock_validator_instance = MagicMock()
        mock_filter.return_value = mock_filter_instance
        mock_validator.return_value = mock_validator_instance

        pipeline = SecureLLMPipeline()

        assert pipeline.input_filter == mock_filter_instance
        assert pipeline.output_validator == mock_validator_instance


class TestUtilityFunctions:
    """Test class for utility functions."""

    def test_create_structured_prompt(self):
        """Test structured prompt creation."""
        system_instructions = "You are a helpful assistant"
        user_data = "Rephrase this text"

        prompt = create_structured_prompt(system_instructions, user_data)

        assert "SYSTEM_INSTRUCTIONS:" in prompt
        assert "USER_DATA_TO_PROCESS:" in prompt
        assert system_instructions in prompt
        assert user_data in prompt
        assert "CRITICAL:" in prompt

    def test_generate_system_prompt(self):
        """Test system prompt generation."""
        role = "writing assistant"
        task = "rephrase text"

        prompt = generate_system_prompt(role, task)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "assistant" in prompt.lower()
        assert "rephrase" in prompt.lower()

    def test_create_structured_prompt_empty_inputs(self):
        """Test structured prompt with empty inputs."""
        prompt = create_structured_prompt("", "")

        assert "SYSTEM_INSTRUCTIONS:" in prompt
        assert "USER_DATA_TO_PROCESS:" in prompt
        assert "CRITICAL:" in prompt

    def test_generate_system_prompt_empty_inputs(self):
        """Test system prompt generation with empty inputs."""
        prompt = generate_system_prompt("", "")

        assert isinstance(prompt, str)
        # Should still return a valid prompt even with empty inputs
