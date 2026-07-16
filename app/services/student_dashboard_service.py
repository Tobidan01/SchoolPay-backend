from decimal import Decimal

from sqlalchemy.orm import Session, selectinload

from app.models.student import Student
from app.schemas.student_dashboard import (
    StudentDashboardPageResponse,
    StudentDashboardResponse,
    StudentPageSummary,
    
)


class StudentDashboardService:

    @staticmethod
    def get_students(
        db: Session,
    ) -> StudentDashboardPageResponse:

        students = (
            db.query(Student)
            .options(
                selectinload(Student.invoices),
                selectinload(Student.school_class),
                selectinload(Student.virtual_account),
                selectinload(Student.credits),
            )
            .order_by(
                Student.created_at.desc()
            )
            .all()
        )

        student_rows: list[
            StudentDashboardResponse
        ] = []

        total_expected_revenue = Decimal("0")
        total_outstanding_balance = Decimal("0")
        paid_students = 0

        for student in students:
            invoices = student.invoices or []
            credits = student.credits or []

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

            available_credit = sum(
                (
                    Decimal(
                        str(
                            credit.remaining_amount
                        )
                    )
                    for credit in credits
                ),
                Decimal("0"),
            )

            # ----------------------------------
            # Financial status
            # ----------------------------------

            if not invoices:
                payment_status = "NO_INVOICE"

            elif outstanding_balance == Decimal("0"):

                if available_credit > Decimal("0"):
                    payment_status = "OVERPAID"

                else:
                    payment_status = "PAID"

            elif amount_paid > Decimal("0"):
                payment_status = "PARTIALLY_PAID"

            else:
                payment_status = "UNPAID"

            # A student who is overpaid has also
            # fully settled all invoices.
            if payment_status in {
                "PAID",
                "OVERPAID",
            }:
                paid_students += 1

            full_name = " ".join(
                part
                for part in [
                    student.first_name,
                    student.middle_name,
                    student.last_name,
                ]
                if part
            )

            student_row = StudentDashboardResponse(
                id=student.id,
                admission_number=(
                    student.admission_number
                ),
                full_name=full_name,
                class_name=(
                    student.school_class.name
                    if student.school_class
                    else None
                ),
                photo_url=student.photo_url,
                virtual_account=(
                    student.virtual_account
                    .account_number
                    if student.virtual_account
                    else None
                ),
                expected_fee=expected_fee,
                amount_paid=amount_paid,
                outstanding_balance=(
                    outstanding_balance
                ),
                available_credit=(
                    available_credit
                ),
                payment_status=(
                    payment_status
                ),
            )

            student_rows.append(student_row)

            total_expected_revenue += (
                expected_fee
            )

            total_outstanding_balance += (
                outstanding_balance
            )

        summary = StudentPageSummary(
            total_students=len(student_rows),
            expected_revenue=(
                total_expected_revenue
            ),
            outstanding_balance=(
                total_outstanding_balance
            ),
            paid_students=paid_students,
        )

        return StudentDashboardPageResponse(
            summary=summary,
            students=student_rows,
        )