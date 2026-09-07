from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthCheck(BaseModel):
    status: str
    service: str
    version: str


@router.get("/health", response_model=HealthCheck)
async def health():
    return HealthCheck(status="healthy", service="career-copilot-api", version="1.0.0")
