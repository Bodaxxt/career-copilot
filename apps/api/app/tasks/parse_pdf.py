"""
Celery task for parsing PDF CVs.
مهمة معالجة واستخراج محتوى السيرة الذاتية عبر الذكاء الاصطناعي في الخلفية.
"""

import asyncio
import logging
import uuid
from typing import Any, Dict
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.audit import AuditLog
from app.models.cv import CV
from app.services.file_storage import LocalFileStorage

logger = logging.getLogger(__name__)
storage = LocalFileStorage()


def mock_gemini_parse_pdf(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Mock Gemini AI response extracting structured information from CV PDF.
    """
    return {
        "summary": "Fullstack Software Engineer with 3+ years experience in Python & TypeScript.",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Next.js", "Docker", "Redis", "Celery"],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Tech Solutions",
                "duration": "2023 - Present",
                "description": "Developed backend microservices with FastAPI and Celery.",
            }
        ],
        "education": [
            {
                "degree": "B.Sc. in Computer Science",
                "institution": "Cairo University",
                "year": "2023",
            }
        ],
        "projects": [
            {
                "name": "Career Copilot",
                "description": "AI-powered career coaching and ATS analysis platform.",
            }
        ],
    }


async def _save_parsed_cv_async(cv_id_str: str, parsed_data: Dict[str, Any]) -> None:
    """Async database helper to persist parsed data and update CV status."""
    async with AsyncSessionLocal() as db:
        cv_uuid = uuid.UUID(cv_id_str)
        result = await db.execute(select(CV).where(CV.id == cv_uuid))
        cv = result.scalar_one_or_none()
        if cv:
            cv.status = "parsed"
            cv.raw_text = str(parsed_data.get("summary", ""))
            await db.commit()


async def _record_failure_audit_async(cv_id_str: str, error_msg: str) -> None:
    """Async database helper to record task failure in audit logs and update CV status."""
    async with AsyncSessionLocal() as db:
        cv_uuid = uuid.UUID(cv_id_str)
        result = await db.execute(select(CV).where(CV.id == cv_uuid))
        cv = result.scalar_one_or_none()
        if cv:
            cv.status = "failed"

        audit = AuditLog(
            user_id=cv.user_id if cv else None,
            action="CV_PARSE_FAILED",
            entity_type="cv",
            entity_id=cv_id_str,
            details=f"Permanent failure in parse_pdf_task: {error_msg}",
        )
        db.add(audit)
        await db.commit()


@shared_task(
    bind=True,
    name="app.tasks.parse_pdf.parse_pdf_task",
    queue="pdf",
    max_retries=3,
    default_retry_delay=5,
)
def parse_pdf_task(self, cv_id: str, file_path_relative: str) -> Dict[str, Any]:
    """
    Background job to read uploaded PDF, parse content via AI, and chain embeddings task.
    """
    logger.info(f"Starting parse_pdf_task for CV: {cv_id}, file: {file_path_relative}")

    try:
        # 1. Resolve file path and read bytes
        local_path = storage.get_file_path(file_path_relative)
        if not local_path or not local_path.exists():
            raise FileNotFoundError(f"File not found on disk at: {file_path_relative}")

        with open(local_path, "rb") as f:
            pdf_bytes = f.read()

        # 2. Parse PDF with mock Gemini service
        parsed_result = mock_gemini_parse_pdf(pdf_bytes, local_path.name)

        # 3. Save parsed result to database and update status to 'parsed'
        asyncio.run(_save_parsed_cv_async(cv_id, parsed_result))
        logger.info(f"Successfully parsed CV: {cv_id}")

        # 4. Chain to generate_embeddings_task
        from app.tasks.generate_embeddings import generate_embeddings_task

        generate_embeddings_task.delay(cv_id)

        return {
            "cv_id": cv_id,
            "status": "parsed",
            "parsed_data": parsed_result,
        }

    except Exception as exc:
        logger.warning(
            f"parse_pdf_task failed for CV {cv_id} (Attempt {self.request.retries + 1}/3): {exc}"
        )
        try:
            # Attempt retry with exponential backoff
            raise self.retry(exc=exc, countdown=5 * (2**self.request.retries))
        except MaxRetriesExceededError:
            # Retries exhausted -> Manual DLQ handling & Audit Log
            error_str = str(exc)
            logger.error(f"[DLQ] parse_pdf_task permanently failed for CV {cv_id}. Routing to DLQ.")
            asyncio.run(_record_failure_audit_async(cv_id, error_str))

            from app.tasks.dlq import handle_dlq_task

            handle_dlq_task.delay(
                "parse_pdf_task",
                {"cv_id": cv_id, "file_path_relative": file_path_relative},
                error_str,
            )
            raise exc
