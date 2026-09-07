"""
Queue Service for enqueuing and tracking background Celery tasks.
خدمة إدارة وجدولة المهام الخلفية واسترجاع حالتها.
"""

from typing import Any, Dict, Union
from uuid import UUID
from celery.result import AsyncResult

from app.core.celery_app import celery_app
from app.tasks.parse_pdf import parse_pdf_task
from app.tasks.generate_embeddings import generate_embeddings_task


class QueueService:
    """
    Service to dispatch background jobs and query Celery task states.
    """

    @staticmethod
    def enqueue_cv_parsing(cv_id: Union[UUID, str], file_path_relative: str) -> str:
        """
        Dispatches parse_pdf_task and returns the Celery task ID.
        """
        task = parse_pdf_task.delay(str(cv_id), file_path_relative)
        return str(task.id)

    @staticmethod
    def enqueue_embedding(cv_id: Union[UUID, str]) -> str:
        """
        Dispatches generate_embeddings_task and returns the Celery task ID.
        """
        task = generate_embeddings_task.delay(str(cv_id))
        return str(task.id)

    @staticmethod
    def get_task_status(task_id: str) -> Dict[str, Any]:
        """
        Queries Celery backend for current status, result, or error of a task.
        """
        async_result = AsyncResult(task_id, app=celery_app)
        state = async_result.state
        result = None
        error = None

        if async_result.successful():
            result = async_result.result
        elif async_result.failed():
            error = str(async_result.result)

        return {
            "task_id": task_id,
            "status": state,
            "result": result,
            "error": error,
        }
