"""
JobDescription and JobRequirement models.
نماذج توصيف الوظائف ومتطلباتها المفصلة.
"""

import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.job_board import JobBoardSource
    from app.models.skill import SkillTaxonomy
    from app.models.submission import Submission
    from app.models.ats import ATSScoringHistory
    from app.models.bulk_match import BulkMatchJob


class JobDescription(Base, TimestampMixin):
    """
    جدول توصيف الوظائف
    """

    __tablename__ = "job_descriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    employment_type: Mapped[str] = mapped_column(
        Enum(
            "full_time",
            "part_time",
            "internship",
            "contract",
            "remote",
            name="employment_type",
            create_type=False,
        ),
        default="full_time",
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_board_sources.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    external_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    salary_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    source: Mapped[Optional["JobBoardSource"]] = relationship(back_populates="jobs")
    requirements: Mapped[List["JobRequirement"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
    submissions: Mapped[List["Submission"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
    ats_scores: Mapped[List["ATSScoringHistory"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
    bulk_matches: Mapped[List["BulkMatchJob"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class JobRequirement(Base, TimestampMixin):
    """
    جدول متطلبات الوظيفة المفصلة بدلاً من حقل JSON
    """

    __tablename__ = "job_requirements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_descriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    requirement_text: Mapped[str] = mapped_column(Text, nullable=False)
    skill_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skill_taxonomy.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    job: Mapped["JobDescription"] = relationship(back_populates="requirements")
    taxonomy_skill: Mapped[Optional["SkillTaxonomy"]] = relationship(
        back_populates="job_requirements"
    )
