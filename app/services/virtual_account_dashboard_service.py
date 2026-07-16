from decimal import Decimal

from sqlalchemy.orm import Session, selectinload

from app.models.student import Student
from app.models.virtual_account import VirtualAccount
from app.schemas.virtual_account import (
    VirtualAccountDashboardItem,
    VirtualAccountDashboardPageResponse,
    VirtualAccountDashboardSummary,
)


class VirtualAccountDashboardService:

    @staticmethod
    def get_virtual_accounts(
        db: Session,
    ) -> VirtualAccountDashboardPageResponse:

        virtual_accounts = (
            db.query(VirtualAccount)
            .options(
                selectinload(
                    VirtualAccount.student
                ).selectinload(
                    Student.school_class
                ),
                selectinload(
                    VirtualAccount.student
                ).selectinload(
                    Student.invoices
                ),
            )
            .order_by(
                VirtualAccount.created_at.desc()
            )
            .all()
        )

        account_rows: list[
            VirtualAccountDashboardItem
        ] = []

        total_collected = Decimal("0")
        total_outstanding = Decimal("0")
        active_accounts = 0

        for virtual_account in virtual_accounts:

            student = virtual_account.student

            if student is None:
                continue

            invoices = student.invoices or []

            expected_fee = sum(
                (
                    Decimal(
                        str(invoice.amount_due)
                    )
                    for invoice in invoices
                ),
                Decimal("0"),
            )

            amount_paid = sum(
                (
                    Decimal(
                        str(invoice.amount_paid)
                    )
                    for invoice in invoices
                ),
                Decimal("0"),
            )

            outstanding_balance = sum(
                (
                    Decimal(
                        str(invoice.balance)
                    )
                    for invoice in invoices
                ),
                Decimal("0"),
            )

            full_name = " ".join(
                part
                for part in [
                    student.first_name,
                    student.middle_name,
                    student.last_name,
                ]
                if part
            )

            account_status = (
                virtual_account.status
                or (
                    "ACTIVE"
                    if virtual_account.is_active
                    else "INACTIVE"
                )
            )

            if str(account_status).upper() == "ACTIVE":
                active_accounts += 1

            account_rows.append(
                VirtualAccountDashboardItem(
                    id=virtual_account.id,
                    student_id=student.id,

                    full_name=full_name,

                    class_name=(
                        student.school_class.name
                        if student.school_class
                        else None
                    ),

                    photo_url=student.photo_url,

                    bank_name=(
                        virtual_account.bank_name
                        or "Nomba"
                    ),

                    account_number=(
                        virtual_account.account_number
                    ),

                    expected_fee=expected_fee,
                    amount_paid=amount_paid,

                    outstanding_balance=(
                        outstanding_balance
                    ),

                    status=str(account_status),
                )
            )

            total_collected += amount_paid
            total_outstanding += outstanding_balance

        summary = VirtualAccountDashboardSummary(
            total_accounts=len(account_rows),

            active_accounts=active_accounts,

            amount_collected=total_collected,

            outstanding_balance=(
                total_outstanding
            ),
        )

        return VirtualAccountDashboardPageResponse(
            summary=summary,
            virtual_accounts=account_rows,
        )