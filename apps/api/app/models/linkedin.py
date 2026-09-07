"""
LinkedInData and LinkedInSkill models.
نماذج بيانات لينكد إن والمهارات المستخرجة بشكل مفصل Normalized.
"""

import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class LinkedInData(Base, TimestampMixin):
    """
    جدول بيانات حساب لينكد إن للمستخدم
    """

    __tablename__ = "linkedin_data"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    profile_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    headline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    connections_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="linkedin_data")
    skills: Mapped[List["LinkedInSkill"]] = relationship(
        back_populates="linkedin_data", cascade="all, delete-orphan"
    )


class LinkedInSkill(Base, TimestampMixin):
    """
    جدول مهارات لينكد إن المفصلة بدلاً من JSON
    """

    __tablename__ = "linkedin_skills"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    linkedin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("linkedin_data.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    endorsements_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    linkedin_data: Mapped["LinkedInData"] = relationship(back_populates="skills")
