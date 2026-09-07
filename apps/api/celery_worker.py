"""
Celery worker entrypoint for Career Copilot.
نقطة انطلاق مشغل مهام Celery (Worker).
"""

from app.core.celery_app import celery_app
import app.tasks  # noqa: F401

__all__ = ["celery_app"]

if __name__ == "__main__":
    celery_app.start()
