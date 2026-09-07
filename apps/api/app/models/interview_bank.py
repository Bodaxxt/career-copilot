"""
InterviewQuestion and InterviewResponse models.
نماذج بنك أسئلة المقابلات وإجابات وتقييمات الذكاء الاصطناعي لكل سؤال.
"""

import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.interview import Interview
    from app.models.user import User


class InterviewQuestion(Base, TimestampMixin):
    """
    جدول بنك أسئلة المقابلات التقنية والسلوكية
    """

    __tablename__ = "interview_questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(
        Enum("easy", "medium", "hard", name="question_difficulty", create_type=False),
        default="medium",
        nullable=False,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    expected_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    responses: Mapped[List["InterviewResponse"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )


class InterviewResponse(Base, TimestampMixin):
    """
    جدول إجابات المستخدمين وتقييم الذكاء الاصطناعي لكل سؤال
    """

    __tablename__ = "interview_responses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_evaluation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    interview: Mapped["Interview"] = relationship(back_populates="responses")
    question: Mapped["InterviewQuestion"] = relationship(back_populates="responses")
    user: Mapped["User"] = relationship(back_populates="interview_responses")
