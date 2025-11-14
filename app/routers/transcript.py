from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.cache import cache_service
from app.services.summarizer import SummarizerService
from app.services.youtube_service import YouTubeService

router = APIRouter()
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
    url_or_id: str

class TranscriptResponse(BaseModel):
    summary: str

@router.post("/summarize", response_model=TranscriptResponse)
async def summarize_transcript(request: TranscriptRequest):
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