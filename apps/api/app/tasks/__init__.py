"""
Background tasks package initialization.
استيراد وتسجيل كافة مهام Celery في النظام.
"""

from app.tasks.parse_pdf import parse_pdf_task
from app.tasks.generate_embeddings import generate_embeddings_task
from app.tasks.bulk_match import bulk_match_task
from app.tasks.dlq import handle_dlq_task

__all__ = [
    "parse_pdf_task",
    "generate_embeddings_task",
    "bulk_match_task",
    "handle_dlq_task",
]
