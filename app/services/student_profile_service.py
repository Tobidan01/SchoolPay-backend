from decimal import Decimal
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.student_credit import StudentCredit
from app.models.virtual_account import VirtualAccount

from app.schemas import student
from app.schemas.student_profile import (
    StudentProfileResponse,
    ParentInformation,
    FeeSummary,
    PaymentHistoryItem,
    InvoiceHistoryItem,
    CreditItem,
    PaymentTimelineItem,
)

from app.schemas.student import StudentResponse
from app.schemas.virtual_account import VirtualAccountResponse



class StudentProfileService:

    @staticmethod
    def get_student_profile(
        db: Session,
        student_id: UUID,
    ):
        
        student = db.get(Student, student_id)

        print("FOUND:", student)
        if student is None:
            return None     
        
        virtual_account = (
            db.query(VirtualAccount)
            .filter(
                VirtualAccount.student_id == student_id
            )
            .first()
        )

        expected_fee = (
            db.query(
                func.coalesce(
                    func.sum(Invoice.amount_due),
                    Decimal("0"),
                )
            )
            .filter(
                Invoice.student_id == student_id
            )
            .scalar()
        )

        amount_paid = (
            db.query(
                func.coalesce(
                    func.sum(Invoice.amount_paid),
                    Decimal("0"),
                )
            )
            .filter(
                Invoice.student_id == student_id
            )
            .scalar()
        )

        outstanding = (
            db.query(
                func.coalesce(
                    func.sum(Invoice.balance),
                    Decimal("0"),
                )
            )
            .filter(
                Invoice.student_id == student_id
            )
            .scalar()
        )

        payments = (
            db.query(Payment)
            .filter(
                Payment.student_id == student_id
            )
            .order_by(
                Payment.paid_at.desc()
            )
            .all()
        )

        invoices = (
            db.query(Invoice)
            .filter(
                Invoice.student_id == student_id
            )
            .order_by(
                Invoice.created_at.desc()
            )
            .all()
        )

        credits = (
            db.query(StudentCredit)
            .filter(
                StudentCredit.student_id == student_id
            )
            .all()
        )

        payment_history = [
            PaymentHistoryItem(
                id=p.id,
                amount=p.amount,
                status=p.status,
                method=p.payment_method,
                paid_at=p.paid_at,
            )
            for p in payments
        ]

        invoice_history = [
            InvoiceHistoryItem(
                id=i.id,
                invoice_number=i.invoice_number,
                expected=i.amount_due,
                paid=i.amount_paid,
                balance=i.balance,
                status=i.status,
            )
            for i in invoices
        ]

        credit_history = [
            CreditItem(
                id=c.id,
                amount=c.amount,
                remaining_amount=c.remaining_amount,
                reason=c.reason,
                created_at=c.created_at,
            )
            for c in credits
        ]

        timeline = [
            PaymentTimelineItem(
                title=f"Payment - {p.payment_method}",
                amount=p.amount,
                date=p.paid_at,
            )
            for p in payments
        ]

        return StudentProfileResponse(
            student=StudentResponse.model_validate(student),

            parent=ParentInformation(
                name=student.parent_name,
                phone=student.parent_phone,
                email=student.parent_email,
            ),

            virtual_account=(
                VirtualAccountResponse.model_validate(virtual_account)
                if virtual_account
                else None
            ),

            fee_summary=FeeSummary(
                expected_fee=expected_fee,
                amount_paid=amount_paid,
                outstanding_balance=outstanding,
            ),

            payment_history=payment_history,

            invoices=invoice_history,

            credits=credit_history,

            payment_timeline=timeline,
        )