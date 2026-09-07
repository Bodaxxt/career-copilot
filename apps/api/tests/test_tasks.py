"""
Unit and integration tests for Celery background tasks, QueueService, and task endpoints.
اختبارات مهام Celery والتحقق من حالات النجاح وإعادة المحاولة وتوجيه الـ DLQ.
"""

import io
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import ASGITransport, AsyncClient

from app.core.auth import get_current_user
from app.database import get_db
from app.main import app
from app.models.user import User
from app.tasks.parse_pdf import parse_pdf_task, mock_gemini_parse_pdf
from app.tasks.generate_embeddings import generate_embeddings_task, generate_mock_vector_embedding
from app.tasks.bulk_match import bulk_match_task
from app.tasks.dlq import handle_dlq_task
from app.services.queue_service import QueueService


@pytest.fixture
def mock_user():
    return User(
        id=uuid.uuid4(),
        clerk_id="user_test_celery_123",
        email="test_celery@career-copilot.app",
        name="Celery Tester",
        role="student",
        profile_completed=True,
    )


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


def test_mock_gemini_parse_pdf():
    """Verify mock Gemini parser returns required structured CV sections."""
    result = mock_gemini_parse_pdf(b"%PDF-1.4 sample", "resume.pdf")
    assert "skills" in result
    assert "experience" in result
    assert "education" in result
    assert "projects" in result
    assert "summary" in result
    assert len(result["skills"]) > 0


def test_generate_mock_vector_embedding():
    """Verify mock vector generator generates 1536-dimensional embeddings."""
    vector = generate_mock_vector_embedding("Python and FastAPI software development")
    assert len(vector) == 1536
    assert isinstance(vector[0], float)


@patch("app.tasks.parse_pdf.storage.get_file_path")
@patch("app.tasks.parse_pdf._save_parsed_cv_async")
@patch("app.tasks.generate_embeddings.generate_embeddings_task.delay")
def test_parse_pdf_task_success(mock_chain, mock_save_db, mock_get_path, tmp_path):
    """
    Test parse_pdf_task reads PDF, parses with mock, saves to DB, and chains embeddings.
    """
    # Create temp PDF file
    test_pdf = tmp_path / "test_cv.pdf"
    test_pdf.write_bytes(b"%PDF-1.4 dummy resume content")
    mock_get_path.return_value = test_pdf
    mock_save_db.return_value = None

    cv_id = str(uuid.uuid4())
    result = parse_pdf_task(cv_id, "uploads/test_cv.pdf")

    assert result["cv_id"] == cv_id
    assert result["status"] == "parsed"
    assert "parsed_data" in result
    mock_chain.assert_called_once_with(cv_id)


@patch("app.tasks.generate_embeddings._process_embeddings_async")
def test_generate_embeddings_task_success(mock_process_db):
    """
    Test generate_embeddings_task calculates vector embeddings and stores chunks.
    """
    mock_process_db.return_value = 4
    cv_id = str(uuid.uuid4())
    result = generate_embeddings_task(cv_id)

    assert result["cv_id"] == cv_id
    assert result["status"] == "ready"
    assert result["embedding_status"] == "completed"
    assert result["chunks_created"] == 4


def test_bulk_match_task():
    """Verify bulk match task placeholder runs and returns completed state."""
    job_id = str(uuid.uuid4())
    result = bulk_match_task(job_id)
    assert result["job_id"] == job_id
    assert result["status"] == "completed"


def test_handle_dlq_task():
    """Verify dead letter queue handler routes and logs permanently failed tasks."""
    payload = {"cv_id": "123", "file_path_relative": "uploads/cv.pdf"}
    result = handle_dlq_task("parse_pdf_task", payload, "File corrupted")
    assert result["status"] == "routed_to_dlq"
    assert result["task_name"] == "parse_pdf_task"


@patch("app.services.queue_service.AsyncResult")
def test_queue_service_get_task_status(mock_async_result):
    """Test QueueService returns task status from Celery AsyncResult backend."""
    mock_inst = MagicMock()
    mock_inst.state = "SUCCESS"
    mock_inst.successful.return_value = True
    mock_inst.failed.return_value = False
    mock_inst.result = {"status": "parsed"}
    mock_async_result.return_value = mock_inst

    status_data = QueueService.get_task_status("mock-task-123")
    assert status_data["task_id"] == "mock-task-123"
    assert status_data["status"] == "SUCCESS"
    assert status_data["result"] == {"status": "parsed"}
    assert status_data["error"] is None


@pytest.mark.asyncio
@patch("app.services.queue_service.QueueService.get_task_status")
async def test_task_status_endpoint(mock_get_status):
    """Test GET /api/v1/tasks/{task_id}/status endpoint."""
    mock_get_status.return_value = {
        "task_id": "task_abc_456",
        "status": "SUCCESS",
        "result": {"chunks": 4},
        "error": None,
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/tasks/task_abc_456/status")

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "task_abc_456"
    assert data["status"] == "SUCCESS"
    assert data["result"] == {"chunks": 4}


@pytest.mark.asyncio
@patch("app.services.queue_service.QueueService.enqueue_cv_parsing")
async def test_upload_returns_task_id(mock_enqueue, mock_user, mock_db_session):
    """
    Test that POST /api/v1/cvs/upload enqueues background job and returns task_id immediately.
    """
    mock_enqueue.return_value = "celery-task-uuid-789"
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            pdf_content = b"%PDF-1.4 dummy pdf content for background parsing"
            files = {"file": ("student_cv.pdf", io.BytesIO(pdf_content), "application/pdf")}
            headers = {"Authorization": "Bearer test-mock-token"}
            response = await ac.post("/api/v1/cvs/upload", files=files, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "uploaded"
        assert data["task_id"] == "celery-task-uuid-789"
        assert "cv_id" in data
        assert data["original_filename"] == "student_cv.pdf"
        mock_enqueue.assert_called_once()
    finally:
        app.dependency_overrides.clear()
