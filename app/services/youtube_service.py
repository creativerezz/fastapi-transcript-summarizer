from typing import Optional
import asyncio
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from app.services.cache import cache_service

class YouTubeService:
    def __init__(self):
        self.cache_service = cache_service

    async def fetch_transcript(self, video_id: str) -> Optional[str]:
        cached_transcript = self.cache_service.get_transcript(video_id)
        if cached_transcript:
            return cached_transcript

        try:
            loop = asyncio.get_running_loop()
            transcript = await loop.run_in_executor(None, YouTubeTranscriptApi.get_transcript, video_id)
            transcript_text = " ".join([entry['text'] for entry in transcript])
            self.cache_service.set_transcript(video_id, transcript_text)
            return transcript_text
        except Exception as e:
            print(f"Error fetching transcript for video ID {video_id}: {e}")
            return None

    async def fetch_transcript_by_url(self, url: str) -> Optional[str]:
        video_id = self.extract_video_id(url)
        if video_id:
            return await self.fetch_transcript(video_id)
        return None

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        if "youtube.com/watch?v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        return None