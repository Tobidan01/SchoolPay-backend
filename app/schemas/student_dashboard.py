from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class StudentDashboardResponse(BaseModel):
    id: UUID
    admission_number: str
    full_name: str

    class_name: str | None = None
    photo_url: str | None = None
    virtual_account: str | None = None

    expected_fee: Decimal
    amount_paid: Decimal
    outstanding_balance: Decimal
    available_credit: Decimal

    payment_status: str

class StudentPageSummary(BaseModel):
    total_students: int
    expected_revenue: Decimal
    outstanding_balance: Decimal
    paid_students: int


class StudentDashboardPageResponse(BaseModel):
    summary: StudentPageSummary
    students: list[StudentDashboardResponse]    