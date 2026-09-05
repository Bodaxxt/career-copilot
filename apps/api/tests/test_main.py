import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "career-copilot-api"


@pytest.mark.asyncio
async def test_career_assessment():
    transport = ASGITransport(app=app)
    payload = {
        "skills": ["TypeScript", "Next.js", "Python", "FastAPI"],
        "target_role": "Fullstack Developer",
        "experience_years": 3,
    }
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/assessment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "matchScore" in data
    assert len(data["strengths"]) == 4
