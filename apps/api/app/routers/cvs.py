"""
CV router for uploading and managing CV files.
مسارات معالجة ورفع ملفات السير الذاتية.
"""

from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database import get_db
from app.models.cv import CV
from app.models.user import User
from app.schemas.cv import CVUploadResponse
from app.services.file_storage import LocalFileStorage

router = APIRouter(prefix="/cvs", tags=["CVs"])
storage = LocalFileStorage()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB in bytes


@router.post(
    "/upload",
    response_model=CVUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload CV PDF file",
    description="Upload a candidate's CV in PDF format (max 10MB).",
)
async def upload_cv(
    file: UploadFile = File(..., description="PDF file of the CV (max 10MB)"),
    title: Optional[str] = Form(None, description="Optional custom title for the CV"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CVUploadResponse:
    """
    Endpoint to receive, validate, store, and record a candidate's CV.
    """
    original_filename = file.filename or "cv.pdf"

    # 1. Validate file format (must be PDF)
    is_pdf_ext = original_filename.lower().endswith(".pdf")
    allowed_mimes = (
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream",
    )
    is_pdf_mime = file.content_type in allowed_mimes
    if not is_pdf_ext or (file.content_type and not is_pdf_mime):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF files are allowed.",
        )

    # 2. Read file content and validate size (Max 10MB)
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum allowed size is 10MB.",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded.",
        )

    # 3. Store file locally
    file_url = await storage.save_file(content, original_filename)

    # 4. Save CV record in DB
    cv_record = CV(
        user_id=current_user.id,
        title=title if title else original_filename,
        file_url=file_url,
        is_primary=False,
    )
    db.add(cv_record)
    await db.commit()
    await db.refresh(cv_record)

    return CVUploadResponse(
        cv_id=str(cv_record.id),
        file_url=cv_record.file_url or file_url,
        status="parsed_pending",
        original_filename=original_filename,
    )
