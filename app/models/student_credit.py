import uuid
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Numeric,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class CreditReason(str, Enum):
    OVERPAYMENT = "OVERPAYMENT"
    MANUAL_ADJUSTMENT = "MANUAL_ADJUSTMENT"
    REFUND_REVERSAL = "REFUND_REVERSAL"


class StudentCredit(Base):
    __tablename__ = "student_credits"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.id"),
        nullable=False,
    )

    payment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payments.id"),
        nullable=False,
    )

    amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    remaining_amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    reason = Column(
        SqlEnum(CreditReason),
        nullable=False,
        default=CreditReason.OVERPAYMENT,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    student = relationship(
        "Student",
        back_populates="credits",
    )

    payment = relationship(
        "Payment",
        back_populates="credit",
    )

    usages = relationship(
        "StudentCreditUsage",
        back_populates="credit",
        cascade="all, delete-orphan",
)
    

    usages = relationship(
        "StudentCreditUsage",
        back_populates="credit",
        cascade="all, delete-orphan",
)
    
