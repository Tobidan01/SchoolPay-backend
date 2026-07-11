from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.virtual_account import VirtualAccount
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.student_credit import StudentCredit

from app.schemas.dashboard import (
    DashboardSummaryResponse,
    InvoiceSummary,
    PaymentSummary,
    CreditSummary,
    RevenueCard,
    ReconciliationCard,
    TrendItem,
    RecentPaymentItem,
    OutstandingStudentItem,
)


class DashboardService:

    @staticmethod
    def summary(db: Session):

        total_students = db.query(Student).count()

        total_virtual_accounts = (
            db.query(VirtualAccount)
            .count()
        )

        total_invoices = db.query(
            Invoice
        ).count()


        paid_invoices = (
            db.query(Invoice)
            .filter(
                Invoice.balance == 0
            )
            .count()
        )


        unpaid_invoices = (
            db.query(Invoice)
            .filter(
                Invoice.balance > 0
            )
            .count()
        )

        expected_revenue = (
            db.query(
                func.coalesce(
                    func.sum(
                        Invoice.amount_due
                    ),
                    Decimal("0")
                )
            )
            .scalar()
        )


        collected_revenue = (
            db.query(
                func.coalesce(
                    func.sum(
                        Payment.amount
                    ),
                    Decimal("0")
                )
            )
            .scalar()
        )

        outstanding_balance = (
            db.query(
                func.coalesce(
                    func.sum(
                        Invoice.balance
                    ),
                    Decimal("0")
                )
            )
            .scalar()
        )


        available_credit = (
            db.query(
                func.coalesce(
                    func.sum(
                        StudentCredit.remaining_amount
                    ),
                    Decimal("0")
                )
            )
            .scalar()
        )

        collection_rate = 0

        if expected_revenue > 0:

            collection_rate = round(
                float(
                    collected_revenue
                    /
                    expected_revenue
                    *
                    100
                ),
                2,
            )


        return DashboardSummaryResponse(
            students=total_students,
            virtual_accounts=total_virtual_accounts,
            invoices=InvoiceSummary(
            total=total_invoices,
            paid=paid_invoices,
            unpaid=unpaid_invoices,
        ),

            payments=PaymentSummary(
            total_amount=collected_revenue,
        ),

            credits=CreditSummary(
            available=available_credit,
        ),

            revenue=RevenueCard(
            expected=expected_revenue,
            collected=collected_revenue,
            outstanding=outstanding_balance,
            collection_rate=collection_rate,
        ),

            reconciliation=ReconciliationCard(
            accuracy=100,
            paid=paid_invoices,
            underpaid=0,
            overpaid=0,
            pending=unpaid_invoices,
        ),

            trend=[],

            recent_payments=[],

            top_outstanding=[],
        )