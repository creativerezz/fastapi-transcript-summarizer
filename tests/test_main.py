from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "metrics" in response.text

def test_summarize_transcript():
    # Replace with a valid YouTube URL or ID for testing
    youtube_url = "https://www.youtube.com/watch?v=example"
    response = client.post("/summarize", json={"url": youtube_url})
    assert response.status_code == 200
    assert "summary" in response.json()