# FastAPI Transcript Summarizer

This project is a FastAPI application that fetches YouTube video transcripts, summarizes them using a map-reduce style pipeline with a language model, and caches the results. It provides health and metrics endpoints for monitoring.

## Features

- Fetches transcripts from YouTube using video URLs or IDs.
- Caches transcripts and summaries for efficient retrieval.
- Summarizes transcripts in manageable chunks.
- Health check and metrics endpoints for monitoring.

## Project Structure

```
fastapi-transcript-summarizer
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── metrics.py
│   │   └── transcript.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── cache.py
│   │   ├── summarizer.py
│   │   └── youtube_service.py
│   └── utils
│       ├── __init__.py
│       └── chunking.py
├── tests
│   ├── __init__.py
│   └── test_main.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/fastapi-transcript-summarizer.git
   cd fastapi-transcript-summarizer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the FastAPI application, execute the following command:

```
uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

### API Endpoints

- **Health Check**
  - `GET /health`
  - Returns the health status of the application.

- **Metrics**
  - `GET /metrics`
  - Exposes application metrics for monitoring.

- **Summarize Transcript**
  - `POST /summarize`
  - Accepts a JSON payload with a YouTube URL or ID and returns the summarized transcript.

## Testing

To run the tests, use the following command:

```
pytest
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.