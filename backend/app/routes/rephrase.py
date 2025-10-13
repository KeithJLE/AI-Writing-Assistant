"""Rephrase API routes."""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

from ..models.requests import RephraseRequest, RephraseResponse
from ..services.rephrase import rephrase_service

router = APIRouter(prefix="/v1/rephrase", tags=["rephrase"])


@router.post("", response_model=RephraseResponse)
async def create_rephrase(request: RephraseRequest) -> RephraseResponse:
    """
    Create a new rephrase request and return request_id.

    Args:
        request: The rephrase request containing text and styles

    Returns:
        Response with request_id
    """
    request_id = rephrase_service.create_request(request.text, request.styles)
    return RephraseResponse(request_id=request_id)


@router.get("/stream")
async def stream_rephrase(request: Request, request_id: str):
    """
    Stream rephrase results via SSE.

    Args:
        request: FastAPI request object
        request_id: Unique identifier for the rephrase request

    Returns:
        StreamingResponse with SSE events
    """
    if not request_id:
        raise HTTPException(status_code=400, detail="request_id is required")

    return StreamingResponse(
        rephrase_service.stream_rephrase(request, request_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.delete("/{request_id}")
async def cancel_rephrase(request_id: str):
    """
    Cancel an active rephrase request.

    Args:
        request_id: Unique identifier for the rephrase request

    Returns:
        Success message
    """
    from ..services.rephrase import cancel_request

    if cancel_request(request_id):
        return {"message": f"Request {request_id} canceled successfully"}

    raise HTTPException(
        status_code=404, detail="Request not found or already completed"
    )
