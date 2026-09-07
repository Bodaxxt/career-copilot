"""
Task schemas for Celery job status responses.
مخططات Pydantic لحالات المهام الخلفية.
"""

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class TaskStatusResponse(BaseModel):
    """
    Response model for querying background task status.
    """

    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
