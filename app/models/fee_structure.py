import uuid
from decimal import Decimal

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class FeeStructure(Base):
    __tablename__ = "fee_structures"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    class_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "classes.id",
            ondelete="CASCADE",
        ),
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
        String(150),
        nullable=False,
    )

    status = Column(
        String(20),
        nullable=False,
        default="ACTIVE",
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

    school_class = relationship(
        "Class",
        back_populates="fee_structures",
    )

    items = relationship(
        "FeeStructureItem",
        back_populates="fee_structure",
        cascade="all, delete-orphan",
    )

    @property
    def total_amount(self) -> Decimal:
        return sum(
            (
                item.amount
                for item in self.items
            ),
            Decimal("0.00"),
        )