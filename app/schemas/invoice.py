from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

from app.models.invoice import InvoiceStatus
from app.schemas.student import StudentInvoiceResponse, StudentSummary, StudentSummary


# ==========================
# Invoice Item
# ==========================

class InvoiceItemCreate(BaseModel):
    fee_structure_item_id: UUID | None = None
    title: str
    description: str | None = None
    quantity: int = 1
    unit_price: Decimal


class InvoiceItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    quantity: int
    unit_price: Decimal
    amount: Decimal
# ==========================
# Invoice
# ==========================

class InvoiceCreate(BaseModel):
    student_id: UUID
    session: str
    term: str
    due_date: date




class InvoiceResponse(BaseModel):
    id: UUID
    invoice_number: str

    session: str
    term: str

    title: str
    description: str | None

    amount_due: Decimal
    amount_paid: Decimal
    balance: Decimal

    status: str

    due_date: date
    created_at: datetime

    student: StudentSummary

    items: list[InvoiceItemResponse]

    model_config = ConfigDict(from_attributes=True)


class InvoiceGenerateResponse(BaseModel):
    message: str

    invoice: InvoiceResponse

    student: StudentInvoiceResponse

    items: list[InvoiceItemResponse]    