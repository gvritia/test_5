import os

from fastapi import APIRouter

from app.models.model_health import HealthResponse

router = APIRouter(tags=["health"])

HEALTH_RESPONSES = {
    200: {
        "description": "Application is running.",
    }
}


@router.get("/health", response_model=HealthResponse, responses=HEALTH_RESPONSES)
def get_health() -> HealthResponse:
    return HealthResponse(status="ok", env=os.getenv("APP_ENV", "local"))
