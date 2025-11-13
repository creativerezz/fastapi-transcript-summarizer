from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.cache import cache_service
from app.services.summarizer import SummarizerService
from app.services.youtube_service import YouTubeService

router = APIRouter()
cache_svc = cache_service
summarizer_service = SummarizerService()
youtube_service = YouTubeService()

class TranscriptRequest(BaseModel):
    url_or_id: str

class TranscriptResponse(BaseModel):
    summary: str

@router.post("/summarize", response_model=TranscriptResponse)
async def summarize_transcript(request: TranscriptRequest):
    cache_key = request.url_or_id
    cached_summary = cache_svc.get(cache_key)
    
    if cached_summary:
        return TranscriptResponse(summary=cached_summary)

    try:
        transcript = await youtube_service.fetch_transcript(request.url_or_id)
        summary = await summarizer_service.summarize_transcript(transcript)
        cache_svc.set(cache_key, summary)
        return TranscriptResponse(summary=summary)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))