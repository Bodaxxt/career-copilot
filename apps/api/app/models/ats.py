"""
ATSScoringHistory model.
نموذج سجل نتائج فحص وتوافق السيرة الذاتية مع متطلبات الوظائف (ATS).
"""

import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.cv import CV
    from app.models.job import JobDescription


class ATSScoringHistory(Base, TimestampMixin):
    """
    جدول سجل تقييمات التوافق مع أنظمة التوظيف ATS
    """

    __tablename__ = "ats_scoring_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cv_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cvs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_descriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    skills_match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    experience_match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    keywords_missing: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    cv: Mapped["CV"] = relationship(back_populates="ats_scores")
    job: Mapped["JobDescription"] = relationship(back_populates="ats_scores")
