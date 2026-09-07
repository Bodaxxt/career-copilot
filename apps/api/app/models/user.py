"""
User and University models.
نماذج المستخدمين والجامعات مع كامل العلاقات والفهارس.
"""

import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.cv import CV
    from app.models.submission import Submission
    from app.models.interview import Interview
    from app.models.linkedin import LinkedInData
    from app.models.github import GitHubData
    from app.models.subscription import Subscription
    from app.models.notification import Notification
    from app.models.audit import AuditLog
    from app.models.interview_bank import InterviewResponse
    from app.models.university_invite import UniversityInvite
    from app.models.bulk_match import BulkMatchJob


class University(Base, TimestampMixin):
    """
    جدول الجامعات الشريكة
    """

    __tablename__ = "universities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(100), default="Egypt", nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    users: Mapped[List["User"]] = relationship(
        back_populates="university", cascade="all, delete-orphan"
    )
    invites: Mapped[List["UniversityInvite"]] = relationship(
        back_populates="university", cascade="all, delete-orphan"
    )
    bulk_match_jobs: Mapped[List["BulkMatchJob"]] = relationship(
        back_populates="university", cascade="all, delete-orphan"
    )


class User(Base, TimestampMixin):
    """
    جدول المستخدمين المرتبط بـ Clerk والمشروع
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum(
            "student",
            "admin",
            "recruiter",
            "university_admin",
            name="user_role",
            create_type=False,
        ),
        default="student",
        nullable=False,
        index=True,
    )
    university_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("universities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    profile_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    university: Mapped[Optional["University"]] = relationship(back_populates="users")
    cvs: Mapped[List["CV"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    submissions: Mapped[List["Submission"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    interviews: Mapped[List["Interview"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    linkedin_data: Mapped[Optional["LinkedInData"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    github_data: Mapped[Optional["GitHubData"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    subscriptions: Mapped[List["Subscription"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="user")
    interview_responses: Mapped[List["InterviewResponse"]] = relationship(back_populates="user")
