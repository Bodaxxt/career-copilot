"""
Dead Letter Queue (DLQ) task and error handler.
معالجة المهام الفاشلة بعد استنفاد محاولات الإعادة وتسجيلها في سجل التدقيق.
"""

import logging
from typing import Any, Dict
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.dlq.handle_dlq_task", queue="dlq")
def handle_dlq_task(task_name: str, payload: Dict[str, Any], error_message: str) -> Dict[str, Any]:
    """
    Handles poisoned or repeatedly failing tasks routed to DLQ.
    """
    logger.error(
        f"[DLQ] Task '{task_name}' failed permanently. Payload: {payload}. Error: {error_message}"
    )
    return {
        "status": "routed_to_dlq",
        "task_name": task_name,
        "payload": payload,
        "error": error_message,
    }
