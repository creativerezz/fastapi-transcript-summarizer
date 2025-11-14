from fastapi import APIRouter, Response
from prometheus_client import Counter, generate_latest

router = APIRouter(tags=["Monitoring"])

# Metrics for tracking requests
REQUEST_COUNT = Counter("request_count", "Total number of requests", ["method", "endpoint"])

@router.get(
    "/metrics",
    summary="Get Metrics",
    description="Retrieve Prometheus metrics for monitoring the application",
    response_description="Prometheus-formatted metrics"
)
async def get_metrics():
    """
    Prometheus metrics endpoint for monitoring.
    
    Returns Prometheus-formatted metrics including request counts and other application metrics.
    This endpoint is typically used by monitoring systems like Prometheus or Grafana.
    
    Returns:
        Response: Prometheus-formatted metrics text
    """
    REQUEST_COUNT.labels(method="GET", endpoint="/metrics").inc()
    return Response(content=generate_latest(), media_type="text/plain")

# @router.middleware("http")
# async def track_requests(request, call_next):
#     response = await call_next(request)
#     REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
#     return response