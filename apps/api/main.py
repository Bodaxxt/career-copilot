from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os

app = FastAPI(
    title="Career Copilot API",
    description="Backend API powered by FastAPI for Career Copilot",
    version="1.0.0",
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Schemas
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class AssessmentRequest(BaseModel):
    skills: List[str] = Field(..., min_items=1, description="List of technical and soft skills")
    target_role: Optional[str] = Field(None, description="Target career role")
    experience_years: Optional[int] = Field(0, ge=0)


class AssessmentResponse(BaseModel):
    matchScore: float
    strengths: List[str]
    recommendedRoles: List[str]
    skillGaps: List[str]


@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend service status."""
    return HealthResponse(
        status="healthy",
        service="career-copilot-api",
        version="1.0.0",
    )


@app.post("/api/v1/assessment", response_model=AssessmentResponse, tags=["Assessment"])
async def career_assessment(request: AssessmentRequest):
    """Analyze user skills and calculate career match insights."""
    if not request.skills:
        raise HTTPException(status_code=400, detail="Skills list cannot be empty")

    # Simple sample heuristic logic for demonstration
    skill_count = len(request.skills)
    score = min(100.0, 50.0 + (skill_count * 10))

    return AssessmentResponse(
        matchScore=score,
        strengths=request.skills,
        recommendedRoles=["Fullstack Engineer", "AI Solutions Architect"],
        skillGaps=["System Design", "Cloud Native Architectures"],
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
