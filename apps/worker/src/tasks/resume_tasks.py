from src.main import celery_app
import time

@celery_app.task(name="tasks.process_resume_pdf")
def process_resume_pdf(resume_id: str, file_path: str):
    """Background task to extract text and analyze embeddings for uploaded resumes."""
    print(f"Starting background extraction for resume: {resume_id}")
    time.sleep(2)  # Simulating heavy AI parsing & embedding generation
    print(f"Finished parsing resume: {resume_id}")
    return {
        "resume_id": resume_id,
        "status": "completed",
        "embeddings_stored": True,
    }
