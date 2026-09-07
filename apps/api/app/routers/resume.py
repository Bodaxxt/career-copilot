from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/resumes", tags=["Resumes"])


class ResumeAnalyzeRequest(BaseModel):
    content: str
    target_job_description: str | None = None


class ResumeAnalyzeResponse(BaseModel):
    score: int
    matched_keywords: List[str]
    missing_keywords: List[str]
    suggestions: List[str]


@router.post("/analyze", response_model=ResumeAnalyzeResponse)
async def analyze_resume(req: ResumeAnalyzeRequest):
    return ResumeAnalyzeResponse(
        score=82,
        matched_keywords=["FastAPI", "React", "Docker", "TypeScript"],
        missing_keywords=["Kubernetes", "GraphQL"],
        suggestions=[
            "Add measurable metrics to past work experiences.",
            "Highlight experience with distributed queue systems like Celery/Redis.",
        ],
    )
