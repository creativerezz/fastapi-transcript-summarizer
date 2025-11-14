from typing import List
import asyncio
import hashlib
from openai import AsyncOpenAI
from app.utils.chunking import chunk_text
from app.services.cache import cache_service
from app.config import get_settings

settings = get_settings()

class SummarizerService:
    def __init__(self):
        self.cache = cache_service
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required but not set. Please set it in your environment variables.")
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def summarize_transcript(self, transcript: str) -> str:
        key = hashlib.md5(transcript.encode()).hexdigest()
        cached_summary = await self.cache.get_summary(key)
        if cached_summary:
            return cached_summary

        chunks = chunk_text(transcript, max_chunk_size=settings.max_chars_per_chunk)
        summaries = await self._summarize_chunks(chunks)
        final_summary = await self._combine_summaries(summaries)

        await self.cache.set_summary(key, final_summary)
        return final_summary

    async def _summarize_chunks(self, chunks: List[str]) -> List[str]:
        return await asyncio.gather(*(self._summarize_chunk(chunk) for chunk in chunks))

    async def _summarize_chunk(self, chunk: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_chunk_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes text concisely."},
                    {"role": "user", "content": f"Summarize the following text:\n\n{chunk}"}
                ],
                max_tokens=200,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Failed to summarize chunk: {str(e)}")

    async def _combine_summaries(self, summaries: List[str]) -> str:
        combined = ' '.join(summaries)
        # If combined summary is too long, summarize it further
        if len(combined) > settings.max_chars_per_chunk:
            try:
                response = await self.client.chat.completions.create(
                    model=settings.openai_reduce_model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                        {"role": "user", "content": f"Create a concise summary of the following summaries:\n\n{combined}"}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                # If final summarization fails, return the combined summaries
                return combined
        return combined