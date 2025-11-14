from typing import List
import asyncio
import hashlib
from transformers import pipeline
from app.utils.chunking import chunk_text
from app.services.cache import cache_service

class SummarizerService:
    def __init__(self):
        self.cache = cache_service
        self.summarizer = pipeline("summarization")

    async def summarize_transcript(self, transcript: str) -> str:
        key = hashlib.md5(transcript.encode()).hexdigest()
        cached_summary = await self.cache.get_summary(key)
        if cached_summary:
            return cached_summary

        chunks = chunk_text(transcript)
        summaries = await self._summarize_chunks(chunks)
        final_summary = self._combine_summaries(summaries)

        await self.cache.set_summary(key, final_summary)
        return final_summary

    async def _summarize_chunks(self, chunks: List[str]) -> List[str]:
        return await asyncio.gather(*(self._summarize_chunk(chunk) for chunk in chunks))

    async def _summarize_chunk(self, chunk: str) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._sync_summarize, chunk)

    def _sync_summarize(self, chunk: str) -> str:
        return self.summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text']

    def _combine_summaries(self, summaries: List[str]) -> str:
        return ' '.join(summaries)