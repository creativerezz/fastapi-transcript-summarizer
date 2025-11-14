from typing import Optional, List, Dict
import asyncio
import json
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from app.services.cache import cache_service, get_redis_client
from app.config import get_settings

settings = get_settings()

# --- Configure youtube-transcript-api with optional Webshare proxies ---
def _build_ytt_client() -> YouTubeTranscriptApi:
    """
    Build a YouTubeTranscriptApi client.
    If WEBSHARE_USERNAME / WEBSHARE_PASSWORD are set, use Webshare proxies.
    Otherwise, use direct connection.
    """
    if settings.webshare_username and settings.webshare_password:
        proxy_config = WebshareProxyConfig(
            proxy_username=settings.webshare_username,
            proxy_password=settings.webshare_password,
        )
        return YouTubeTranscriptApi(proxy_config=proxy_config)
    else:
        return YouTubeTranscriptApi()

_ytt_client = _build_ytt_client()

def extract_video_id(url_or_id: str) -> str:
    """Extract a YouTube video ID from a URL or ID string."""
    # Already looks like an ID
    if len(url_or_id) == 11 and "/" not in url_or_id and "?" not in url_or_id:
        return url_or_id
    
    parsed = urlparse(url_or_id)
    if parsed.hostname in ("youtu.be",):
        return parsed.path.lstrip("/")
    
    qs = parse_qs(parsed.query)
    if "v" in qs:
        return qs["v"][0]
    
    # Fallback for old-style parsing
    if "youtube.com/watch?v=" in url_or_id:
        return url_or_id.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url_or_id:
        return url_or_id.split("youtu.be/")[1].split("?")[0]
    
    raise ValueError("Cannot extract video id from input")

def _fetch_transcript_blocking(video_id: str, language: str = "en") -> List[Dict]:
    """
    Blocking call that uses the global _ytt_client, which may be proxy-backed.
    """
    transcript_list = _ytt_client.list_transcripts(video_id)
    # Prefer manual transcript if available; otherwise generated
    try:
        t = transcript_list.find_manually_created_transcript([language])
    except Exception:
        t = transcript_list.find_generated_transcript([language])
    return t.fetch()

async def fetch_transcript_async(video_id: str, language: str = "en") -> List[Dict]:
    """Fetch transcript asynchronously using executor."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, _fetch_transcript_blocking, video_id, language
    )

async def get_or_fetch_transcript(video_id: str, language: str = "en") -> List[Dict]:
    """Get transcript from cache or fetch from YouTube."""
    key = f"transcript:{video_id}:{language}"
    client = await get_redis_client()
    
    cached = await client.get(key)
    if cached:
        return json.loads(cached)
    
    transcript = await fetch_transcript_async(video_id, language)
    await client.set(
        key,
        json.dumps(transcript),
        ex=settings.cache_ttl_transcript_seconds,
    )
    return transcript

def transcript_to_text(transcript: List[Dict]) -> str:
    """Convert transcript list to text string."""
    parts = sorted(transcript, key=lambda x: x["start"])
    return " ".join(p["text"].strip() for p in parts if p["text"].strip())

class YouTubeService:
    def __init__(self):
        self.cache_service = cache_service

    async def fetch_transcript(self, url_or_id: str, language: str = "en") -> Optional[str]:
        """Fetch transcript from YouTube, using cache if available."""
        try:
            video_id = extract_video_id(url_or_id)
        except ValueError:
            return None
        
        # Check cache first
        cached_transcript = await self.cache_service.get_transcript(video_id)
        if cached_transcript:
            return cached_transcript

        try:
            # Fetch transcript (may use Webshare proxies if configured)
            transcript = await get_or_fetch_transcript(video_id, language)
            transcript_text = transcript_to_text(transcript)
            
            # Cache the text version
            await self.cache_service.set_transcript(video_id, transcript_text)
            return transcript_text
        except Exception as e:
            print(f"Error fetching transcript for video ID {video_id}: {e}")
            return None

    async def fetch_transcript_by_url(self, url: str) -> Optional[str]:
        """Fetch transcript by URL (alias for fetch_transcript)."""
        return await self.fetch_transcript(url)

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from URL (backward compatibility)."""
        try:
            return extract_video_id(url)
        except ValueError:
            return None