from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.cache import cache_service
from app.services.summarizer import SummarizerService
from app.services.youtube_service import YouTubeService

router = APIRouter(tags=["Transcript"])
cache_svc = cache_service
_summarizer_service = None
youtube_service = YouTubeService()

def get_summarizer_service():
    """Lazy-load summarizer service to avoid startup errors if OpenAI key is not set."""
    global _summarizer_service
    if _summarizer_service is None:
        _summarizer_service = SummarizerService()
    return _summarizer_service

class TranscriptRequest(BaseModel):
    url_or_id: str = Field(
        ...,
        description="YouTube video URL or video ID",
        json_schema_extra={"example": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
    )

class TranscriptResponse(BaseModel):
    summary: str = Field(..., description="The summarized transcript of the YouTube video")

@router.post(
    "/summarize",
    response_model=TranscriptResponse,
    summary="Summarize Transcript",
    description="Fetch and summarize a YouTube video transcript",
    responses={
        200: {
            "description": "Successfully summarized transcript",
            "content": {
                "application/json": {
                    "example": {
                        "summary": "This video discusses the main topics covered in the transcript..."
                    }
                }
            }
        },
        400: {
            "description": "Bad request - invalid URL or summarization failed",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to fetch transcript"}
                }
            }
        },
        404: {
            "description": "Transcript not found for the given video",
            "content": {
                "application/json": {
                    "example": {"detail": "Transcript not found"}
                }
            }
        },
        422: {
            "description": "Validation error - invalid request format"
        }
    }
)
async def summarize_transcript(request: TranscriptRequest):
    """
    Summarize a YouTube video transcript.
    
    This endpoint:
    1. Checks cache for existing summary
    2. Fetches the transcript from YouTube if not cached
    3. Summarizes the transcript using OpenAI API
    4. Caches the result for future requests
    
    Args:
        request: TranscriptRequest containing YouTube URL or video ID
        
    Returns:
        TranscriptResponse: The summarized transcript
        
    Raises:
        HTTPException: 404 if transcript not found, 400 for other errors
    """
    cache_key = request.url_or_id
    cached_summary = await cache_svc.get_summary(cache_key)
    
    if cached_summary:
        return TranscriptResponse(summary=cached_summary)

    try:
        transcript = await youtube_service.fetch_transcript(request.url_or_id)
        if not transcript:
            raise HTTPException(status_code=404, detail="Transcript not found")
        summarizer_service = get_summarizer_service()
        summary = await summarizer_service.summarize_transcript(transcript)
        await cache_svc.set_summary(cache_key, summary)
        return TranscriptResponse(summary=summary)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))