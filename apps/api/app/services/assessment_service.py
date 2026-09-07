from typing import List
from app.schemas.assessment import AssessmentResponse


class AssessmentService:
    @staticmethod
    def evaluate_skills(skills: List[str], target_role: str | None = None) -> AssessmentResponse:
        count = len(skills)
        score = min(100.0, 45.0 + (count * 11.5))

        roles = ["Fullstack Engineer", "DevOps Architect", "AI Engineer"]
        if target_role:
            roles.insert(0, target_role)

        return AssessmentResponse(
            matchScore=score,
            strengths=skills,
            recommendedRoles=roles[:3],
            skillGaps=["High-Level System Design", "Microservices Security"],
        )
