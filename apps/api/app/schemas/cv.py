"""
CV Pydantic schemas.
مخططات Pydantic الخاصة بالسير الذاتية ورفع الملفات.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CVUploadResponse(BaseModel):
    """
    Response model returned after successfully uploading a CV.
    """

    cv_id: str
    file_url: str
    status: str = "parsed_pending"
    original_filename: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CVOut(BaseModel):
    """
    Detailed CV model response.
    """

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    file_url: Optional[str] = None
    is_primary: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
