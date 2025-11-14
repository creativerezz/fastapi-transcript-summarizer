from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, metrics, transcript

app = FastAPI(
    title="FastAPI Transcript Summarizer",
    description="A FastAPI application that fetches YouTube video transcripts and summarizes them using OpenAI's API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(transcript.router)

@app.get(
    "/",
    summary="Root",
    description="Welcome endpoint with API information",
    tags=["General"]
)
async def root():
    """
    Root endpoint that returns a welcome message.
    
    Returns:
        dict: Welcome message with API information
    """
    return {"message": "Welcome to the FastAPI Transcript Summarizer!"}