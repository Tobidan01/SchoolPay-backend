import uuid
from decimal import Decimal

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class FeeStructureItem(Base):
    __tablename__ = "fee_structure_items"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    fee_structure_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "fee_structures.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    title = Column(
        String(150),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    quantity = Column(
        Integer,
        nullable=False,
        default=1,
    )

    unit_price = Column(
        Numeric(12, 2),
        nullable=False,
    )

    fee_structure = relationship(
        "FeeStructure",
        back_populates="items",
    )

    @property
    def amount(self) -> Decimal:
        return (
            Decimal(str(self.quantity))
            * Decimal(str(self.unit_price))
        )