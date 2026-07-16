from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.student_credit import (
    CreditReason,
    StudentCredit,
)


class StudentCreditService:

    @staticmethod
    def create(
        db: Session,
        *,
        student_id,
        payment_id,
        amount: Decimal,
    ) -> StudentCredit:

        if amount <= 0:
            raise ValueError(
                "Credit amount must be greater than zero."
            )

        credit = StudentCredit(
            student_id=student_id,
            payment_id=payment_id,
            amount=amount,
            remaining_amount=amount,
            reason=CreditReason.OVERPAYMENT,
        )

        db.add(credit)
        db.flush()

        return credit

    @staticmethod
    def get_balance(
        db: Session,
        *,
        student_id,
    ) -> Decimal:

        total = (
            db.query(
                func.coalesce(
                    func.sum(
                        StudentCredit.remaining_amount
                    ),
                    0,
                )
            )
            .filter(
                StudentCredit.student_id == student_id
            )
            .scalar()
        )

        return Decimal(str(total))

    @staticmethod
    def consume_credit(
        db: Session,
        *,
        student_id,
        amount: Decimal,
    ) -> dict:

        if amount <= 0:
            raise ValueError(
                "Amount to consume must be greater than zero."
            )

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

        remaining_to_consume = amount
        consumed_amount = Decimal("0")

        for credit in credits:

            if remaining_to_consume <= 0:
                break

            available_credit = Decimal(
                str(credit.remaining_amount)
            )

            deduction = min(
                available_credit,
                remaining_to_consume,
            )

            credit.remaining_amount = (
                available_credit - deduction
            )

            remaining_to_consume -= deduction
            consumed_amount += deduction

        db.flush()

        return {
            "requested_amount": amount,
            "consumed_amount": consumed_amount,
            "uncovered_amount": remaining_to_consume,
            "fully_covered": remaining_to_consume == 0,
        }