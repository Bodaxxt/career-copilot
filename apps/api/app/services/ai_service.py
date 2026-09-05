import os
from typing import Dict, Any

class AIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")

    async def analyze_resume_text(self, text: str) -> Dict[str, Any]:
        """Analyze resume text extracting insights and recommendations."""
        return {
            "wordCount": len(text.split()),
            "status": "processed",
            "summary": "Resume content contains strong technical foundational skills.",
            "actionVerbsScore": 85,
        }
