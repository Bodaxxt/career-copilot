"""
Celery task for bulk candidate-job matching.
مهمة مطابقة المرشحين مع متطلبات الوظائف بشكل جماعي في الخلفية.
"""

import logging
from typing import Any, Dict
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.bulk_match.bulk_match_task", queue="matching")
def bulk_match_task(job_id: str) -> Dict[str, Any]:
    """
    Placeholder task for bulk matching candidates against job requisitions.
    """
    logger.info(f"[BulkMatch] Executing bulk match job for Job ID: {job_id}")
    return {
        "job_id": job_id,
        "status": "completed",
        "matched_candidates_count": 0,
    }
