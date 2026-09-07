"""
Interview model.
نموذج المقابلات وتفاصيل التقييم.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.submission import Submission
    from app.models.interview_bank import InterviewResponse


class Interview(Base, TimestampMixin):
    """
    جدول المقابلات الوهمية والتجريبية والمقابلة الفعلية
    """

    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    submission_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("submissions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    interview_type: Mapped[str] = mapped_column(
        Enum(
            "technical",
            "behavioral",
            "mock",
            "system_design",
            "hr",
            name="interview_type",
            create_type=False,
        ),
        default="mock",
        nullable=False,
    )
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(
            "scheduled",
            "in_progress",
            "completed",
            "cancelled",
            name="interview_status",
            create_type=False,
        ),
        default="scheduled",
        nullable=False,
        index=True,
    )
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="interviews")
    submission: Mapped[Optional["Submission"]] = relationship(back_populates="interviews")
    responses: Mapped[List["InterviewResponse"]] = relationship(
        back_populates="interview", cascade="all, delete-orphan"
    )
