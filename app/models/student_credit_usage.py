import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class StudentCreditUsage(Base):
    __tablename__ = "student_credit_usages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    credit_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "student_credits.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    invoice_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "invoices.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    amount_used = Column(
        Numeric(12, 2),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    credit = relationship(
        "StudentCredit",
        back_populates="usages",
    )

    invoice = relationship(
        "Invoice",
        back_populates="credit_usages",
    )