"""Request and response models."""

from pydantic import BaseModel, Field


class RephraseRequest(BaseModel):
    """Request model for rephrase endpoint."""

    text: str = Field(..., description="Text to be rephrased")
    styles: list[str] = Field(
        ..., description="List of styles to rephrase the text into"
    )


class RephraseResponse(BaseModel):
    """Response model for rephrase endpoint."""

    request_id: str = Field(
        ..., description="Unique identifier for the rephrase request"
    )
