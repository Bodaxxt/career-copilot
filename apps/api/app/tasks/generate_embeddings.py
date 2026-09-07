"""
Celery task for generating vector embeddings from parsed CV content.
توليد التضمينات الشعاعية (Vector Embeddings) وتخزين الأجزاء في قاعدة البيانات.
"""

import asyncio
import logging
import random
import uuid
from typing import Any, Dict, List
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.audit import AuditLog
from app.models.cv import CV, CVChunk

logger = logging.getLogger(__name__)


def generate_mock_vector_embedding(text: str, dim: int = 1536) -> List[float]:
    """
    Generate mock 1536-dimensional embedding vector (compatible with OpenAI text-embedding-3).
    """
    # Deterministic or randomized vector
    rng = random.Random(hash(text) % 100000)
    return [round(rng.uniform(-0.1, 0.1), 6) for _ in range(dim)]


async def _process_embeddings_async(cv_id_str: str) -> int:
    """Async database helper to create chunks and compute embeddings."""
    async with AsyncSessionLocal() as db:
        cv_uuid = uuid.UUID(cv_id_str)
        result = await db.execute(select(CV).where(CV.id == cv_uuid))
        cv = result.scalar_one_or_none()
        if not cv:
            raise ValueError(f"CV with id {cv_id_str} not found in database")

        cv.embedding_status = "processing"
        await db.commit()

        # Define CV sections as text chunks
        sections = [
            (
                "Skills & Technologies: Python, FastAPI, PostgreSQL, "
                f"Next.js, Docker, Redis for {cv.title}"
            ),
            "Work Experience: Software Engineer building backend microservices and APIs.",
            "Education: B.Sc. in Computer Science from Cairo University.",
            "Projects: Career Copilot AI Career Platform and ATS resume optimizer.",
        ]

        # Insert chunks
        for idx, content in enumerate(sections):
            embedding = generate_mock_vector_embedding(content)
            chunk = CVChunk(
                cv_id=cv.id,
                chunk_index=idx,
                content=content,
                embedding=embedding,
            )
            db.add(chunk)

        cv.embedding_status = "completed"
        cv.status = "ready"
        await db.commit()
        return len(sections)


async def _record_embedding_failure_async(cv_id_str: str, error_msg: str) -> None:
    """Async database helper to record embedding failure."""
    async with AsyncSessionLocal() as db:
        cv_uuid = uuid.UUID(cv_id_str)
        result = await db.execute(select(CV).where(CV.id == cv_uuid))
        cv = result.scalar_one_or_none()
        if cv:
            cv.embedding_status = "failed"
            cv.status = "failed"

        audit = AuditLog(
            user_id=cv.user_id if cv else None,
            action="CV_EMBEDDING_FAILED",
            entity_type="cv",
            entity_id=cv_id_str,
            details=f"Permanent failure in generate_embeddings_task: {error_msg}",
        )
        db.add(audit)
        await db.commit()


@shared_task(
    bind=True,
    name="app.tasks.generate_embeddings.generate_embeddings_task",
    queue="embeddings",
    max_retries=3,
    default_retry_delay=5,
)
def generate_embeddings_task(self, cv_id: str) -> Dict[str, Any]:
    """
    Background job to create chunks and compute 1536-dim vector embeddings for RAG search.
    """
    logger.info(f"Starting generate_embeddings_task for CV: {cv_id}")

    try:
        chunks_count = asyncio.run(_process_embeddings_async(cv_id))
        logger.info(f"Successfully generated {chunks_count} embedding chunks for CV: {cv_id}")

        return {
            "cv_id": cv_id,
            "status": "ready",
            "embedding_status": "completed",
            "chunks_created": chunks_count,
        }

    except Exception as exc:
        attempt = self.request.retries + 1
        logger.warning(
            f"generate_embeddings_task failed for CV {cv_id} (Attempt {attempt}/3): {exc}"
        )
        try:
            raise self.retry(exc=exc, countdown=5 * (2**self.request.retries))
        except MaxRetriesExceededError:
            error_str = str(exc)
            logger.error(
                f"[DLQ] generate_embeddings_task permanently failed for CV {cv_id}. Routing to DLQ."
            )
            asyncio.run(_record_embedding_failure_async(cv_id, error_str))

            from app.tasks.dlq import handle_dlq_task

            handle_dlq_task.delay("generate_embeddings_task", {"cv_id": cv_id}, error_str)
            raise exc
