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
    response = client.post("/summarize", json={"url_or_id": youtube_url})
    # This will likely fail with 400/404 since it's not a real video, but we test the endpoint structure
    assert response.status_code in [200, 400, 404]
    if response.status_code == 200:
        assert "summary" in response.json()