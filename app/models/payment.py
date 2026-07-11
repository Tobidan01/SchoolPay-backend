import uuid
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


class PaymentMethod(str, Enum):
    TRANSFER = "TRANSFER"
    CARD = "CARD"
    POS = "POS"
    CASH = "CASH"


class PaymentProvider(str, Enum):
    NOMBA = "NOMBA"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ==========================================================
    # Relationships
    # ==========================================================

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.id"),
        nullable=False,
    )

    invoice_id = Column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id"),
        nullable=False,
    )

    virtual_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("virtual_accounts.id"),
        nullable=True,
    )

    # ==========================================================
    # References
    # ==========================================================

    internal_reference = Column(
        String(255),
        unique=True,
        nullable=False,
    )

    provider_transaction_id = Column(
        String(255),
        unique=True,
        nullable=True,
    )

    provider_session_id = Column(
        String(255),
        nullable=True,
    )

    # ==========================================================
    # Payment Details
    # ==========================================================

    amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    currency = Column(
        String(3),
        nullable=False,
        default="NGN",
    )

    gateway_fee = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    provider = Column(
        SqlEnum(PaymentProvider),
        nullable=False,
    )

    payment_method = Column(
        SqlEnum(PaymentMethod),
        nullable=False,
    )

    payment_channel = Column(
        String(100),
        nullable=True,
    )

    status = Column(
        SqlEnum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.PENDING,
    )

    # ==========================================================
    # Payer Information
    # ==========================================================

    payer_name = Column(
        String(255),
        nullable=True,
    )

    payer_bank = Column(
        String(255),
        nullable=True,
    )
    
    payer_account_number = Column(
        String(50),
        nullable=True,
    )

    narration = Column(
        String(500),
        nullable=True,
    )

    # ==========================================================
    # Dates
    # ==========================================================

    paid_at = Column(
        DateTime(timezone=True),
        nullable=True,
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

    # ==========================================================
    # Raw Webhook Payload
    # ==========================================================

    raw_payload = Column(
        JSONB,
        nullable=True,
    )

    # ==========================================================
    # Relationships
    # ==========================================================

    student = relationship(
        "Student",
        back_populates="payments",
    )

    invoice = relationship(
        "Invoice",
        back_populates="payments",
    )

    virtual_account = relationship(
        "VirtualAccount",
        back_populates="payments",
    )


    credit = relationship(
        "StudentCredit",
        back_populates="payment",
        uselist=False,
    )

    