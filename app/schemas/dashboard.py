from decimal import Decimal
from datetime import date
from pydantic import BaseModel


class InvoiceSummary(BaseModel):
    total: int
    paid: int
    unpaid: int


class PaymentSummary(BaseModel):
    total_amount: Decimal


class CreditSummary(BaseModel):
    available: Decimal


class RevenueCard(BaseModel):
    expected: Decimal
    collected: Decimal
    outstanding: Decimal
    collection_rate: float


class ReconciliationCard(BaseModel):
    accuracy: float
    paid: int
    underpaid: int
    overpaid: int
    pending: int


class TrendItem(BaseModel):
    period: str
    expected: Decimal
    collected: Decimal
    outstanding: Decimal


class RecentPaymentItem(BaseModel):
    student: str
    invoice_number: str
    amount: Decimal
    status: str
    paid_at: date


class OutstandingStudentItem(BaseModel):
    student: str
    balance: Decimal


class DashboardSummaryResponse(BaseModel):
    students: int
    virtual_accounts: int

    invoices: InvoiceSummary

    payments: PaymentSummary

    credits: CreditSummary

    revenue: RevenueCard

    reconciliation: ReconciliationCard

    trend: list[TrendItem]

    recent_payments: list[RecentPaymentItem]

    top_outstanding: list[OutstandingStudentItem]