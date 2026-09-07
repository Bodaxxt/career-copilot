from pydantic import BaseModel, Field
from typing import List, Optional


class AssessmentRequest(BaseModel):
    skills: List[str] = Field(..., min_length=1, description="List of technical and soft skills")
    target_role: Optional[str] = Field(None, description="Target career role")
    experience_years: Optional[int] = Field(0, ge=0)


class AssessmentResponse(BaseModel):
    matchScore: float
    strengths: List[str]
    recommendedRoles: List[str]
    skillGaps: List[str]
