"""
Subscription and Payment models.
نماذج الاشتراكات والمدفوعات لتسيير الخطط المدفوعة (Stripe).
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Subscription(Base, TimestampMixin):
    """
    جدول الاشتراكات وخطط المستخدمين
    """

    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    plan: Mapped[str] = mapped_column(
        Enum("free", "pro", "enterprise", name="subscription_plan", create_type=False),
        default="free",
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        Enum(
            "active",
            "canceled",
            "past_due",
            "trialing",
            name="subscription_status",
            create_type=False,
        ),
        default="active",
        nullable=False,
        index=True,
    )
    current_period_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_period_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="subscriptions")
    payments: Mapped[List["Payment"]] = relationship(
        back_populates="subscription", cascade="all, delete-orphan"
    )


class Payment(Base, TimestampMixin):
    """
    جدول فواتير وعمليات الدفع
    """

    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(
            "succeeded",
            "failed",
            "pending",
            "refunded",
            name="payment_status",
            create_type=False,
        ),
        default="pending",
        nullable=False,
        index=True,
    )
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )

    # Relationships
    subscription: Mapped["Subscription"] = relationship(back_populates="payments")
