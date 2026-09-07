"""
PyTest unit and integration tests for CV upload endpoint.
اختبارات الرفع والتحقق من الهوية والأحجام المسموحة.
"""

import io
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock

from app.core.auth import get_current_user
from app.database import get_db
from app.main import app
from app.models.user import User


@pytest.fixture
def mock_user():
    """Mock student user."""
    return User(
        id=uuid.uuid4(),
        clerk_id="user_test_mock_123",
        email="test_student@career-copilot.app",
        name="Mock Student",
        role="student",
        profile_completed=True,
    )


@pytest.fixture
def mock_db_session():
    """Mock async DB session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_upload_success(mock_user, mock_db_session):
    """
    Test uploading a valid PDF file with authentication.
    """
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    from unittest.mock import patch

    try:
        with patch(
            "app.services.queue_service.QueueService.enqueue_cv_parsing",
            return_value="mock-celery-task-id",
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                pdf_content = b"%PDF-1.4 dummy pdf content for testing CV upload"
                files = {
                    "file": (
                        "my_resume.pdf",
                        io.BytesIO(pdf_content),
                        "application/pdf",
                    )
                }
                headers = {"Authorization": "Bearer test-mock-token"}
                response = await ac.post("/api/v1/cvs/upload", files=files, headers=headers)

            assert response.status_code == 201
            data = response.json()
            assert "cv_id" in data
            assert "file_url" in data
            assert data["status"] == "uploaded"
            assert data["task_id"] == "mock-celery-task-id"
            assert data["original_filename"] == "my_resume.pdf"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_unauthorized():
    """
    Test uploading without an Authorization header returns 401 Unauthorized.
    """
    # Ensure no dependency overrides
    app.dependency_overrides.clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        pdf_content = b"%PDF-1.4 dummy pdf content"
        files = {"file": ("resume.pdf", io.BytesIO(pdf_content), "application/pdf")}
        response = await ac.post("/api/v1/cvs/upload", files=files)

    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_file_too_large(mock_user, mock_db_session):
    """
    Test uploading a file larger than 10MB returns 413 Request Entity Too Large.
    """
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # 10MB + 1KB
            large_content = b"a" * (10 * 1024 * 1024 + 1024)
            files = {"file": ("large_cv.pdf", io.BytesIO(large_content), "application/pdf")}
            headers = {"Authorization": "Bearer test-mock-token"}
            response = await ac.post("/api/v1/cvs/upload", files=files, headers=headers)

        assert response.status_code == 413
        data = response.json()
        assert "File too large" in data["detail"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_invalid_file_format(mock_user, mock_db_session):
    """
    Test uploading a non-PDF file returns 400 Bad Request.
    """
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            text_content = b"Not a PDF file content"
            files = {"file": ("document.txt", io.BytesIO(text_content), "text/plain")}
            headers = {"Authorization": "Bearer test-mock-token"}
            response = await ac.post("/api/v1/cvs/upload", files=files, headers=headers)

        assert response.status_code == 400
        data = response.json()
        assert "Only PDF files are allowed" in data["detail"]
    finally:
        app.dependency_overrides.clear()
