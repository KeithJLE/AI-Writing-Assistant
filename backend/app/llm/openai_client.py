"""OpenAI client wrapper."""

from openai import OpenAI
from typing import Iterator, Dict, Any

from ..config import settings
from ..security.secure_llm_pipeline import (
    SecureLLMPipeline,
    create_structured_prompt,
    generate_system_prompt,
)


class OpenAIClient:
    """Wrapper for OpenAI client."""

    def __init__(self):
        """Initialize OpenAI client with API key from settings."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.active_streams: Dict[str, Any] = {}
        self.security_pipeline = SecureLLMPipeline()

    def create_completion_stream(
        self,
        request_id: str,
        prompt: str,
        style: str = "",
        model: str = "gpt-4o-mini",
    ) -> Iterator[Any]:
        """
        Create a streaming completion using OpenAI API with security measures.

        Args:
            request_id: Unique identifier for the request
            prompt: The prompt to send to the model
            style: The style for rephrasing (if applicable)
            model: The model to use for completion

        Returns:
            Iterator yielding response objects from OpenAI API
        """
        try:
            # Input validation through security pipeline
            if self.security_pipeline.input_filter.detect_injection(prompt):
                raise ValueError("Input blocked due to security concerns")

            # Sanitize input
            clean_input = self.security_pipeline.input_filter.sanitize_input(
                prompt
            )

            # Create secure system prompt based on style
            style_prompts = {
                "professional": "Rewrite this text in a professional, formal tone suitable for business communications",
                "casual": "Rewrite this text in a casual, friendly tone suitable for informal conversations",
                "polite": "Rewrite this text in a polite, respectful tone suitable for courteous communications",
                "social": "Rewrite this text in a lively, engaging tone suitable for social media",
            }

            task_prompt = style_prompts.get(style, "Rewrite this text")
            system_prompt = generate_system_prompt(
                "a writing assistant",
                f"to {task_prompt} while preserving the original meaning. You should only output the rewritten text, nothing else.",
            )

            # Create structured prompt with clear separation
            user_instruction = f"{task_prompt}: {clean_input}"
            structured_prompt = create_structured_prompt(
                system_prompt, user_instruction
            )

            # Debug:
            # print("=" * 80)
            # print("SENDING TO OPENAI:")
            # print("=" * 80)
            # print(f"Request ID: {request_id}")
            # print(f"Style: {style}")
            # print(f"Model: {model}")
            # print(f"Original input: {prompt}")
            # print(f"Clean input: {clean_input}")
            # print(f"User instruction: {user_instruction}")
            # print("-" * 40)
            # print("FULL STRUCTURED PROMPT:")
            # print("-" * 40)
            # print(structured_prompt)
            # print("=" * 80)

            # Create the stream with OpenAI API
            response_stream = self.client.responses.create(
                model=model,
                input=[{"role": "user", "content": structured_prompt}],
                stream=True,
            )

            # Store the stream for potential cancellation
            self.active_streams[request_id] = response_stream

            return response_stream
        except Exception as e:
            print(f"Error creating completion stream: {str(e)}")
            raise

    def close_stream(self, request_id: str) -> bool:
        """
        Close an active stream.

        Args:
            request_id: Unique identifier for the request

        Returns:
            bool: True if stream was closed, False if not found
        """
        if request_id in self.active_streams:
            try:
                # Close the stream
                self.active_streams[request_id].close()
                print(f"Stream for request {request_id} closed")
                # Remove from active streams
                del self.active_streams[request_id]
                return True
            except Exception as e:
                print(
                    f"Error closing stream for request {request_id}: {str(e)}"
                )
                del self.active_streams[request_id]
                return False
        return False


openai_client = OpenAIClient()
