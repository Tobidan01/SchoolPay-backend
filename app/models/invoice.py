from uuid import uuid4
from enum import Enum as PyEnum



from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class InvoiceStatus(str, PyEnum):
    UNPAID = "UNPAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    OVERPAID = "OVERPAID"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.id"),
        nullable=False,
    )

    invoice_number = Column(
        String(50),
        unique=True,
        nullable=False,
    )

    session = Column(
        String(20),
        nullable=False,
    )

    term = Column(
        String(30),
        nullable=False,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    amount_due = Column(
        Numeric(12, 2),
        nullable=False,
    )

    amount_paid = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    balance = Column(
        Numeric(12, 2),
        nullable=False,
    )

    status = Column(
    SQLEnum(InvoiceStatus),
    nullable=False,
    default=InvoiceStatus.UNPAID
)

    due_date = Column(
        Date,
        nullable=False,
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
        back_populates="invoices",
    )

    items = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )

    payments = relationship(
        "Payment",
        back_populates="invoice",
    )


    credit_usages = relationship(
        "StudentCreditUsage",
        back_populates="invoice",
    )