"""
BulkMatchJob model.
نموذج عمليات المطابقة الجماعية للطلاب مع الوظائف لصالح الجامعات.
"""

import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import University
    from app.models.job import JobDescription


class BulkMatchJob(Base, TimestampMixin):
    """
    جدول مهام المطابقة المجمعة للجامعات والشركاء
    """

    __tablename__ = "bulk_match_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    university_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("universities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_descriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "processing",
            "completed",
            "failed",
            name="bulk_match_status",
            create_type=False,
        ),
        default="pending",
        nullable=False,
        index=True,
    )
    total_candidates: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    matched_candidates: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    results_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    university: Mapped["University"] = relationship(back_populates="bulk_match_jobs")
    job: Mapped["JobDescription"] = relationship(back_populates="bulk_matches")
