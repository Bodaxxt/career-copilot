"""
SkillTaxonomy and SkillAlias models.
نماذج تصنيف المهارات وأسمائها البديلة للتوحيد والبحث الفعال.
"""

import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.cv import CVSkill
    from app.models.job import JobRequirement


class SkillTaxonomy(Base, TimestampMixin):
    """
    جدول قاموس المهارات المعتمدة وتصنيفاتها
    """

    __tablename__ = "skill_taxonomy"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    aliases: Mapped[List["SkillAlias"]] = relationship(
        back_populates="skill", cascade="all, delete-orphan"
    )
    cv_skills: Mapped[List["CVSkill"]] = relationship(back_populates="taxonomy_skill")
    job_requirements: Mapped[List["JobRequirement"]] = relationship(back_populates="taxonomy_skill")


class SkillAlias(Base, TimestampMixin):
    """
    جدول المرادفات والأسماء البديلة للمهارة (مثلاً JS -> JavaScript)
    """

    __tablename__ = "skill_aliases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skill_taxonomy.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    alias_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    # Relationships
    skill: Mapped["SkillTaxonomy"] = relationship(back_populates="aliases")
