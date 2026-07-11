from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.student import StudentResponse
from app.schemas.virtual_account import VirtualAccountResponse

class FeeSummary(BaseModel):
    expected_fee: Decimal
    amount_paid: Decimal
    outstanding_balance: Decimal
class ParentInformation(BaseModel):
    name: str
    phone: str | None
    email: str | None    
class PaymentHistoryItem(BaseModel):

    id: UUID

    amount: Decimal

    status: str

    method: str

    paid_at: datetime

class InvoiceHistoryItem(BaseModel):

    id: UUID

    invoice_number: str

    expected: Decimal

    paid: Decimal

    balance: Decimal

    status: str    

class CreditItem(BaseModel):

    id: UUID

    amount: Decimal

    remaining_amount: Decimal

    reason: str

    created_at: datetime    

class PaymentTimelineItem(BaseModel):

    title: str

    amount: Decimal

    date: datetime    

class StudentProfileResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    student: StudentResponse

    parent: ParentInformation

    virtual_account: VirtualAccountResponse | None

    fee_summary: FeeSummary

    payment_history: list[PaymentHistoryItem]

    invoices: list[InvoiceHistoryItem]

    credits: list[CreditItem]

    payment_timeline: list[PaymentTimelineItem]    
