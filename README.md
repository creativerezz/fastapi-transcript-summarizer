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

## Deployment to Railway

This application is configured for deployment on Railway. Follow these steps:

### Prerequisites

1. A Railway account ([railway.app](https://railway.app))
2. A GitHub repository with your code (or use Railway CLI)

### Deployment Steps

1. **Create a new Railway project:**
   - Go to [railway.app](https://railway.app) and create a new project
   - Select "Deploy from GitHub repo" and choose your repository
   - Or use Railway CLI: `railway init`

2. **Add Redis service (optional but recommended):**
   - In your Railway project, click "New" → "Database" → "Add Redis"
   - Railway will automatically set the `REDIS_URL` environment variable

3. **Set environment variables:**
   - Go to your service → "Variables" tab
   - Add the following required variables:
     - `OPENAI_API_KEY`: Your OpenAI API key
   - Optional variables:
     - `WEBSHARE_PROXY_USERNAME`: Webshare proxy username (if using proxy)
     - `WEBSHARE_PROXY_PASSWORD`: Webshare proxy password (if using proxy)

4. **Deploy:**
   - Railway will automatically detect the `Procfile` and deploy your application
   - The app will be available at the generated Railway domain

5. **Generate a public domain:**
   - Go to your service → "Settings" → "Networking"
   - Click "Generate Domain" to create a public URL

### Environment Variables

The following environment variables can be configured:

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `REDIS_URL` (optional): Redis connection URL (automatically set if you add Redis service)
- `WEBSHARE_PROXY_USERNAME` (optional): Webshare proxy username
- `WEBSHARE_PROXY_PASSWORD` (optional): Webshare proxy password

### Local Development Setup

1. Copy `.env.example` to `.env` (if available)
2. Set your environment variables in `.env`
3. Run: `uvicorn app.main:app --reload`

## License

This project is licensed under the MIT License. See the LICENSE file for details.