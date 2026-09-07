"""
GitHubData and GitHubContribution models.
نماذج بيانات حساب جيت هاب ومساهمات المستودعات المفصلة.
"""

import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class GitHubData(Base, TimestampMixin):
    """
    جدول بيانات حساب جيت هاب للمستخدم
    """

    __tablename__ = "github_data"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    username: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    profile_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    public_repos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_stars: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_forks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="github_data")
    contributions: Mapped[List["GitHubContribution"]] = relationship(
        back_populates="github_data", cascade="all, delete-orphan"
    )


class GitHubContribution(Base, TimestampMixin):
    """
    جدول مساهمات ومستودعات جيت هاب المفصلة بدلاً من JSON
    """

    __tablename__ = "github_contributions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("github_data.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    repo_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    repo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    commits_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pull_requests_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    primary_language: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    github_data: Mapped["GitHubData"] = relationship(back_populates="contributions")
