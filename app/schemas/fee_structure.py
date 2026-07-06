from enum import Enum
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class Term(str, Enum):
    FIRST_TERM = "FIRST_TERM"
    SECOND_TERM = "SECOND_TERM"
    THIRD_TERM = "THIRD_TERM"


class FeeStructureStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class FeeStructureItemCreate(BaseModel):
    title: str
    description: str | None = None
    quantity: int = 1
    unit_price: Decimal

class FeeStructureCreate(BaseModel):
    class_id: UUID
    session: str
    term: Term
    title: str
    items: list[FeeStructureItemCreate]

class FeeStructureItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    item_name: str
    amount: Decimal

class FeeStructureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    class_id: UUID

    session: str

    term: Term

    title: str

    status: FeeStructureStatus

    total_amount: Decimal

    items: list[FeeStructureItemResponse]    


class FeeStructureUpdate(BaseModel):
    session: str | None = None

    term: Term | None = None

    title: str | None = None

    status: FeeStructureStatus | None = None    