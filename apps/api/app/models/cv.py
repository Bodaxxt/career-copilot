"""
CV, CVSkill, and CVChunk models.
نماذج السيرة الذاتية ومهاراتها وأجزاء التضمين الشعاعي (Vector Embeddings).
"""

import uuid
from typing import TYPE_CHECKING, Any, List, Optional
from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.vector import Vector

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.skill import SkillTaxonomy
    from app.models.ats import ATSScoringHistory
    from app.models.submission import Submission


class CV(Base, TimestampMixin):
    """
    جدول السير الذاتية
    """

    __tablename__ = "cvs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="My CV")
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="uploaded", nullable=False, index=True)
    embedding_status: Mapped[Optional[str]] = mapped_column(
        String(50), default="pending", nullable=True, index=True
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="cvs")
    skills: Mapped[List["CVSkill"]] = relationship(
        back_populates="cv", cascade="all, delete-orphan"
    )
    chunks: Mapped[List["CVChunk"]] = relationship(
        back_populates="cv", cascade="all, delete-orphan"
    )
    ats_scores: Mapped[List["ATSScoringHistory"]] = relationship(
        back_populates="cv", cascade="all, delete-orphan"
    )
    submissions: Mapped[List["Submission"]] = relationship(back_populates="cv")


class CVSkill(Base, TimestampMixin):
    """
    جدول مهارات السيرة الذاتية المفصلة بدلاً من تخزين JSON
    """

    __tablename__ = "cv_skills"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cv_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cvs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skill_taxonomy.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    proficiency_level: Mapped[Optional[str]] = mapped_column(
        Enum(
            "beginner",
            "intermediate",
            "advanced",
            "expert",
            name="skill_level",
            create_type=False,
        ),
        nullable=True,
    )
    years_of_experience: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    cv: Mapped["CV"] = relationship(back_populates="skills")
    taxonomy_skill: Mapped[Optional["SkillTaxonomy"]] = relationship(back_populates="cv_skills")


class CVChunk(Base, TimestampMixin):
    """
    جدول أجزاء الـ CV مع تضمينات الـ Vector لمشروع الـ RAG
    """

    __tablename__ = "cv_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cv_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cvs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Any] = mapped_column(Vector(1536), nullable=True)

    # Relationships
    cv: Mapped["CV"] = relationship(back_populates="chunks")
