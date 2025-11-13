from fastapi import APIRouter
from prometheus_client import Counter, generate_latest

router = APIRouter()

# Metrics for tracking requests
REQUEST_COUNT = Counter("request_count", "Total number of requests", ["method", "endpoint"])

@router.get("/metrics")
async def get_metrics():
    REQUEST_COUNT.inc()  # Increment the counter for each request
    return generate_latest()  # Return the latest metrics in Prometheus format

# @router.middleware("http")
# async def track_requests(request, call_next):
#     response = await call_next(request)
#     REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
#     return response