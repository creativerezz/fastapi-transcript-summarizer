from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Health"])

@router.get(
    "/health",
    summary="Health Check",
    description="Check if the API service is running and healthy",
    response_description="Returns the health status of the service"
)
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: A dictionary with status "healthy" if the service is running
    """
    return {"status": "healthy"}