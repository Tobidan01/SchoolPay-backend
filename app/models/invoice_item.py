from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    invoice_id = Column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id"),
        nullable=False,
    )


    fee_structure_item_id = Column(
    UUID(as_uuid=True),
    ForeignKey("fee_structure_items.id"),
    nullable=True,
    )

    title = Column(
        String,
        nullable=False,
    )

    description = Column(
        String(255),
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

    amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    invoice = relationship(
        "Invoice",
        back_populates="items",
    )


    fee_structure_item = relationship(
        "FeeStructureItem",
    )