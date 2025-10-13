"""Rephrase service for handling text rephrasing requests."""

import uuid
import json
from typing import Dict, List, AsyncGenerator, Any

from fastapi import Request

from ..llm.openai_client import openai_client
from ..security.output_validator import OutputValidator

# Store active requests, maybe use something like Redis in prod
active_requests: Dict[str, Dict[str, Any]] = {}


class RephraseService:
    """Service for handling text rephrasing requests."""

    def __init__(self):
        """Initialize the rephrase service with security components."""
        self.output_validator = OutputValidator()

    def create_request(self, text: str, styles: List[str]) -> str:
        """
        Create a new rephrase request.

        Args:
            text: The text to rephrase
            styles: List of styles to rephrase the text into

        Returns:
            request_id: Unique identifier for the request
        """
        request_id = str(uuid.uuid4())

        # Store the request
        active_requests[request_id] = {
            "text": text,
            "styles": styles,
            "status": "created",
        }

        return request_id

    async def stream_rephrase(
        self, request: Request, request_id: str
    ) -> AsyncGenerator[str, None]:
        """
        Stream rephrase results.

        Args:
            request: FastAPI request object
            request_id: Unique identifier for the request

        Yields:
            SSE formatted events
        """
        if request_id not in active_requests:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Request not found'})}\n\n"
            return

        req_data = active_requests[request_id]
        text = req_data["text"]
        styles = req_data["styles"]

        try:
            # Update request status
            active_requests[request_id]["status"] = "processing"

            # Process each style
            for style in styles:
                try:
                    # Stream from OpenAI with enhanced security
                    response_stream = openai_client.create_completion_stream(
                        request_id=request_id, prompt=text, style=style
                    )

                    for event in response_stream:
                        # Check if client disconnected
                        if await request.is_disconnected():
                            print(f"Client disconnected during {style}")
                            # Close the stream to stop token generation
                            openai_client.close_stream(request_id)
                            return

                        # Handle text delta events from OpenAI streaming
                        if event.type == "response.output_text.delta":
                            content = event.delta

                            # Validate output chunk for security
                            if not self.output_validator.validate_output(
                                content
                            ):
                                # Send security error event for frontend to display
                                error_event = {
                                    "type": "error",
                                    "style": style,
                                    "text": "Content blocked due to security concerns. Please try rephrasing your input.",
                                }
                                yield f"data: {json.dumps(error_event)}\n\n"
                                print("errored")
                                # Skip this chunk and continue
                                continue

                            # Send SSE event
                            event_data = {
                                "type": "delta",
                                "style": style,
                                "text": content,
                            }
                            yield f"data: {json.dumps(event_data)}\n\n"

                    # Mark style as complete
                    complete_event = {"type": "complete", "style": style}
                    yield f"data: {json.dumps(complete_event)}\n\n"

                except ValueError as ve:
                    # Handle input validation errors (security blocks)
                    print(f"Validation error for style {style}: {str(ve)}")
                    error_event = {
                        "type": "error",
                        "style": style,
                        "text": "Content blocked due to security concerns. Please try rephrasing your input.",
                    }
                    yield f"data: {json.dumps(error_event)}\n\n"

            # All styles complete
            end_event = {"type": "end"}
            yield f"data: {json.dumps(end_event)}\n\n"

            # Update request status
            if request_id in active_requests:
                active_requests[request_id]["status"] = "completed"

        except Exception as e:
            print(f"Rephrase stream error: {str(e)}")
            error_event = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_event)}\n\n"

            # Update request status
            if request_id in active_requests:
                active_requests[request_id]["status"] = "error"
        finally:
            # Close the stream if it's still active
            openai_client.close_stream(request_id)

            # Clean up request
            if request_id in active_requests:
                del active_requests[request_id]


rephrase_service = RephraseService()


def cancel_request(request_id: str) -> bool:
    """
    Cancel an active rephrase request.

    Args:
        request_id: Unique identifier for the request

    Returns:
        bool: True if request was canceled, False if not found
    """
    if request_id in active_requests:
        # Close the stream
        stream_closed = openai_client.close_stream(request_id)

        # Remove from active requests
        del active_requests[request_id]

        return stream_closed

    return False
