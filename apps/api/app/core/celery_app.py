"""
Celery application instance and configuration.
إعداد وضبط مهام Celery الخلفية والتوجيه للـ Queues.
"""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "career_copilot",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.parse_pdf",
        "app.tasks.generate_embeddings",
        "app.tasks.bulk_match",
        "app.tasks.dlq",
    ],
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.tasks.parse_pdf.*": {"queue": "pdf"},
        "app.tasks.generate_embeddings.*": {"queue": "embeddings"},
        "app.tasks.bulk_match.*": {"queue": "matching"},
        "app.tasks.dlq.*": {"queue": "dlq"},
    },
)
