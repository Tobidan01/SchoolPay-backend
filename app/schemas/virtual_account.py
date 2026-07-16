from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from enum import Enum


class VirtualAccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"

class VirtualAccountCreate(BaseModel):
    student_id: UUID

    account_number: str
    account_name: str
    bank_name: str

    provider: str = "NOMBA"
    provider_reference: str | None = None

    status: VirtualAccountStatus = VirtualAccountStatus.ACTIVE    


class VirtualAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID

    account_number: str
    account_name: str
    bank_name: str

    provider: str
    provider_reference: str | None

    status: VirtualAccountStatus
    is_active: bool


class VirtualAccountDashboardResponse(BaseModel):
    id: UUID
    student_id: UUID

    full_name: str
    class_name: str

    photo_url: str | None = None

    bank_name: str
    account_number: str

    expected_fee: Decimal
    amount_paid: Decimal
    outstanding_balance: Decimal

    status: str   


class VirtualAccountDashboardItem(BaseModel):
    id: UUID
    student_id: UUID

    full_name: str
    class_name: str | None = None
    photo_url: str | None = None

    bank_name: str
    account_number: str

    expected_fee: Decimal
    amount_paid: Decimal
    outstanding_balance: Decimal

    status: str


class VirtualAccountDashboardSummary(BaseModel):
    total_accounts: int
    active_accounts: int
    amount_collected: Decimal
    outstanding_balance: Decimal


class VirtualAccountDashboardPageResponse(BaseModel):
    summary: VirtualAccountDashboardSummary
    virtual_accounts: list[VirtualAccountDashboardItem]     