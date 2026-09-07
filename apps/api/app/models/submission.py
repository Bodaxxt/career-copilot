"""
Submission model.
نموذج تقديم الطلبات للوظائف وتتبع حالتها.
"""

import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job import JobDescription
    from app.models.cv import CV
    from app.models.interview import Interview


class Submission(Base, TimestampMixin):
    """
    جدول تقديم الطلبات ومتابعة مسار التوظيف
    """

    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_descriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cv_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cvs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "applied",
            "interviewing",
            "offered",
            "rejected",
            "withdrawn",
            name="submission_status",
            create_type=False,
        ),
        default="pending",
        nullable=False,
        index=True,
    )
    tailored_cv_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="submissions")
    job: Mapped["JobDescription"] = relationship(back_populates="submissions")
    cv: Mapped[Optional["CV"]] = relationship(back_populates="submissions")
    interviews: Mapped[List["Interview"]] = relationship(
        back_populates="submission", cascade="all, delete-orphan"
    )
