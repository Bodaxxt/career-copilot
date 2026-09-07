import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_career_assessment():
    transport = ASGITransport(app=app)
    payload = {
        "skills": ["Python", "FastAPI", "React", "Next.js"],
        "target_role": "Fullstack AI Engineer",
    }
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/assessment", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "matchScore" in data
    assert data["matchScore"] > 0
    assert "strengths" in data


@pytest.mark.asyncio
async def test_resume_analyzer():
    transport = ASGITransport(app=app)
    payload = {
        "content": "Senior Software Engineer with 5 years experience in Next.js and FastAPI."
    }
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/resumes/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "score" in data
    assert len(data["suggestions"]) > 0
