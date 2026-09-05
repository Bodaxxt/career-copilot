from fastapi import APIRouter
from app.schemas.assessment import AssessmentRequest, AssessmentResponse
from app.services.assessment_service import AssessmentService

router = APIRouter(prefix="/assessment", tags=["Assessment"])

@router.post("", response_model=AssessmentResponse)
async def create_assessment(payload: AssessmentRequest):
    return AssessmentService.evaluate_skills(payload.skills, payload.target_role)
