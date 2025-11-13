from typing import Any, Dict
from functools import lru_cache

class CacheService:
    def __init__(self):
        self.transcript_cache: Dict[str, Any] = {}
        self.summary_cache: Dict[str, Any] = {}

    def get_transcript(self, video_id: str) -> Any:
        return self.transcript_cache.get(video_id)

    def set_transcript(self, video_id: str, transcript: Any) -> None:
        self.transcript_cache[video_id] = transcript

    def get_summary(self, video_id: str) -> Any:
        return self.summary_cache.get(video_id)

    def set_summary(self, video_id: str, summary: Any) -> None:
        self.summary_cache[video_id] = summary

cache_service = CacheService()