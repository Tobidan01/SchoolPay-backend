from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class VirtualAccount(Base):
    __tablename__ = "virtual_accounts"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.id"),
        nullable=False,
        unique=True,  # One account per student
    )

    account_number = Column(
        String(20),
        nullable=False,
        unique=True,
    )

    account_name = Column(
        String(255),
        nullable=False,
    )

    bank_name = Column(
        String(100),
        nullable=False,
    )

    provider = Column(
        String(50),
        nullable=False,
        default="NOMBA",
    )

    provider_reference = Column(
        String(255),
        nullable=True,
)

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )


    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    status = Column(
        String(20),
        nullable=False,
        default="ACTIVE",
    )


    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    student = relationship(
        "Student",
        back_populates="virtual_account",
    )

    payments = relationship(
        "Payment",
        back_populates="virtual_account",
    )