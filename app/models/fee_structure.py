from datetime import datetime
from decimal import Decimal
from decimal import Decimal
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
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
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
    )

    session = Column(
        String,
        nullable=False,
    )

    term = Column(
        String,
        nullable=False,
    )

    title = Column(
        String,
        nullable=False,
    )

    status = Column(
        String,
        default="ACTIVE",
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
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
            (item.amount for item in self.items),
            Decimal("0.00"),
        )