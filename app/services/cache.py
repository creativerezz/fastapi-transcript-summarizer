from typing import Any, Optional
import redis.asyncio as redis
import json
from app.config import get_settings

settings = get_settings()

# Global Redis client instance
_redis_client: Optional[redis.Redis] = None

async def get_redis_client() -> redis.Redis:
    """Get or create Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            str(settings.redis_url),
            decode_responses=True
        )
    return _redis_client

class CacheService:
    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None

    async def _get_client(self) -> redis.Redis:
        """Get Redis client."""
        if self._redis_client is None:
            self._redis_client = await get_redis_client()
        return self._redis_client

    async def get_transcript(self, video_id: str) -> Optional[str]:
        """Get cached transcript."""
        try:
            client = await self._get_client()
            key = f"transcript:{video_id}"
            result = await client.get(key)
            return result
        except Exception as e:
            # Redis not available - return None (cache miss)
            print(f"Redis cache miss (connection error): {type(e).__name__}")
            return None

    async def set_transcript(self, video_id: str, transcript: str) -> None:
        """Cache transcript."""
        try:
            client = await self._get_client()
            key = f"transcript:{video_id}"
            await client.set(key, transcript, ex=settings.cache_ttl_transcript_seconds)
        except Exception as e:
            # Redis not available - silently fail (cache write miss)
            print(f"Redis cache write failed (connection error): {type(e).__name__}")
            pass

    async def get_summary(self, key: str) -> Optional[str]:
        """Get cached summary."""
        try:
            client = await self._get_client()
            cache_key = f"summary:{key}"
            result = await client.get(cache_key)
            return result
        except Exception as e:
            # Redis not available - return None (cache miss)
            print(f"Redis cache miss (connection error): {type(e).__name__}")
            return None

    async def set_summary(self, key: str, summary: str) -> None:
        """Cache summary."""
        try:
            client = await self._get_client()
            cache_key = f"summary:{key}"
            await client.set(cache_key, summary, ex=settings.cache_ttl_summary_seconds)
        except Exception as e:
            # Redis not available - silently fail (cache write miss)
            print(f"Redis cache write failed (connection error): {type(e).__name__}")
            pass

    # Synchronous methods for backward compatibility (will be deprecated)
    def get(self, key: str) -> Optional[str]:
        """Synchronous get - for backward compatibility."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we can't use it synchronously
                # This is a fallback - should be migrated to async
                return None
            return loop.run_until_complete(self.get_summary(key))
        except RuntimeError:
            return None

    def set(self, key: str, value: str) -> None:
        """Synchronous set - for backward compatibility."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we can't use it synchronously
                # This is a fallback - should be migrated to async
                return
            loop.run_until_complete(self.set_summary(key, value))
        except RuntimeError:
            pass

cache_service = CacheService()