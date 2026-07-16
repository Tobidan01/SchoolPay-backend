from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


class PaymentMethod(str, Enum):
    TRANSFER = "TRANSFER"
    CARD = "CARD"
    CASH = "CASH"
    POS = "POS"


class PaymentProvider(str, Enum):
    NOMBA = "NOMBA"


class PaymentBase(BaseModel):
    student_id: UUID
    invoice_id: UUID
    virtual_account_id: Optional[UUID] = None

    amount: Decimal
    currency: str

    provider_transaction_id: Optional[str] = None
    provider_session_id: Optional[str] = None

    provider: PaymentProvider
    payment_method: PaymentMethod
    payment_channel: Optional[str] = None

    status: PaymentStatus

    payer_name: Optional[str] = None
    payer_bank: Optional[str] = None
    payer_account_number: Optional[str] = None
    narration: Optional[str] = None

    gateway_fee: Decimal

    paid_at: Optional[datetime] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentDashboardItem(BaseModel):
    id: UUID
    student_id: UUID

    full_name: str
    class_name: str | None = None
    photo_url: str | None = None

    transaction_reference: str
    amount: Decimal

    bank_name: str | None = None
    payment_method: str

    paid_at: datetime | None = None

    account_number: str | None = None

    status: str


class PaymentDashboardSummary(BaseModel):
    todays_payments: int
    revenue_today: Decimal
    pending_payments: int
    underpaid_payments: int


class PaymentDashboardPageResponse(BaseModel):
    summary: PaymentDashboardSummary
    payments: list[PaymentDashboardItem]    