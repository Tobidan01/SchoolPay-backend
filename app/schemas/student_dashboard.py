from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class StudentDashboardResponse(BaseModel):

    id: UUID

    admission_number: str

    full_name: str

    class_name: str

    virtual_account: str | None

    expected_fee: Decimal

    amount_paid: Decimal

    outstanding_balance: Decimal

    payment_status: str
    photo_url: str | None