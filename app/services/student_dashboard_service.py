from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.virtual_account import VirtualAccount

from app.schemas.student_dashboard import StudentDashboardResponse


class StudentDashboardService:

    @staticmethod
    def get_students(db: Session):

        students = db.query(Student).all()

        response = []

        for student in students:

            virtual_account = (
                db.query(VirtualAccount)
                .filter(
                    VirtualAccount.student_id == student.id
                )
                .first()
            )

            expected_fee = (
                db.query(
                    func.coalesce(
                        func.sum(
                            Invoice.amount_due
                        ),
                        Decimal("0")
                    )
                )
                .filter(
                    Invoice.student_id == student.id
                )
                .scalar()
            )

            amount_paid = (
                db.query(
                    func.coalesce(
                        func.sum(
                            Payment.amount
                        ),
                        Decimal("0")
                    )
                )
                .filter(
                    Payment.student_id == student.id
                )
                .scalar()
            )

            outstanding_balance = max(
                Decimal("0"),
                expected_fee - amount_paid
            )

            if amount_paid == 0:

                status = "PENDING"

            elif amount_paid < expected_fee:

                status = "UNDERPAID"

            elif amount_paid == expected_fee:

                status = "PAID"

            else:

                status = "OVERPAID"

            response.append(

                StudentDashboardResponse(

                    id=student.id,

                    admission_number=student.admission_number,

                    full_name=f"{student.first_name} {student.last_name}",

                    class_name=student.student_class.name,
                    photo_url=student.photo_url,
                    virtual_account=(
                        virtual_account.account_number
                        if virtual_account
                        else None
                    ),

                    expected_fee=expected_fee,

                    amount_paid=amount_paid,

                    outstanding_balance=outstanding_balance,

                    payment_status=status,
                )

            )

        return response