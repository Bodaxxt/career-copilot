"""
Tasks router for querying Celery background jobs status.
مسارات الاستعلام عن حالة المهام الخلفية.
"""

from fastapi import APIRouter, status
from app.schemas.task import TaskStatusResponse
from app.services.queue_service import QueueService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get(
    "/{task_id}/status",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get background task status",
    description="Retrieve real-time status and execution result of a Celery task.",
)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """
    Returns task state (PENDING, STARTED, SUCCESS, FAILURE, RETRY) and results.
    """
    task_info = QueueService.get_task_status(task_id)
    return TaskStatusResponse(
        task_id=task_info["task_id"],
        status=task_info["status"],
        result=task_info["result"],
        error=task_info["error"],
    )
