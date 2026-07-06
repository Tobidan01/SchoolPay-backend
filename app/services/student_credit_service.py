from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.student_credit import (
    StudentCredit,
    CreditReason,
)


class StudentCreditService:

    @staticmethod
    def create(
        db: Session,
        *,
        student_id,
        payment_id,
        amount: Decimal,
    ):

        credit = StudentCredit(
            student_id=student_id,
            payment_id=payment_id,
            amount=amount,
            remaining_amount=amount,
            reason=CreditReason.OVERPAYMENT,
        )

        db.add(credit)
        

        return credit

    @staticmethod
    def get_balance(
        db: Session,
        *,
        student_id,
    ):

        total = (
            db.query(
                func.coalesce(
                    func.sum(StudentCredit.remaining_amount),
                    0,
                )
            )
            .filter(
                StudentCredit.student_id == student_id
            )
            .scalar()
        )

        return Decimal(total)

    @staticmethod
    def consume_credit(
        db: Session,
        *,
        student_id,
        amount: Decimal,
    ):
        credits = (
            db.query(StudentCredit)
            .filter(
                StudentCredit.student_id == student_id,
                StudentCredit.remaining_amount > 0,
        )
        .order_by(
            StudentCredit.created_at.asc()
        )
        .all()
    )

        remaining = amount

        for credit in credits:

            if remaining <= 0:
                break

            deduction = min(
                credit.remaining_amount,
                remaining,
        )

            credit.remaining_amount -= deduction
            remaining -= deduction