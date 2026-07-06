from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.models.payment import (
    Payment,
    PaymentMethod,
    PaymentProvider,
    PaymentStatus,
)
from app.models.student import Student


class PaymentService:

    @staticmethod
    def create_pending_payment(
        db: Session,
        *,
        student: Student,
        invoice: Invoice,
        amount: float,
        internal_reference: str,
        virtual_account_id=None,
    ):

        payment = Payment(
            student_id=student.id,
            invoice_id=invoice.id,
            virtual_account_id=virtual_account_id,

            amount=amount,
            currency="NGN",

            internal_reference=internal_reference,

            provider=PaymentProvider.NOMBA,
            payment_method=PaymentMethod.TRANSFER,
            payment_channel="VIRTUAL_ACCOUNT",

            status=PaymentStatus.PENDING,
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        return payment

    @staticmethod
    def get_by_internal_reference(
        db: Session,
        internal_reference: str,
    ):

        return (
            db.query(Payment)
            .filter(
                Payment.internal_reference == internal_reference
            )
            .first()
        )

    @staticmethod
    def get_by_provider_transaction_id(
        db: Session,
        provider_transaction_id: str,
    ):

        return (
            db.query(Payment)
            .filter(
                Payment.provider_transaction_id
                == provider_transaction_id
            )
            .first()
        )

    @staticmethod
    def mark_success(
        db: Session,
        payment: Payment,
        *,
        provider_transaction_id: str | None = None,
        provider_session_id: str | None = None,
        payer_name: str | None = None,
        payer_bank: str | None = None,
        payer_account_number: str | None = None,
        narration: str | None = None,
        raw_payload: dict,
        paid_at: datetime,
        gateway_fee=0,
    ):

        payment.status = PaymentStatus.SUCCESS
        payment.paid_at = paid_at

        payment.provider_transaction_id = provider_transaction_id
        payment.provider_session_id = provider_session_id

        payment.gateway_fee = gateway_fee

        payment.payer_name = payer_name
        payment.payer_bank = payer_bank
        payment.payer_account_number = payer_account_number

        payment.narration = narration

        payment.raw_payload = raw_payload

        db.commit()
        db.refresh(payment)

        return payment

    @staticmethod
    def mark_failed(
        db: Session,
        payment: Payment,
        *,
        raw_payload: dict,
    ):

        payment.status = PaymentStatus.FAILED
        payment.raw_payload = raw_payload

        db.commit()
        db.refresh(payment)

        return payment

    @staticmethod
    def mark_reversed(
        db: Session,
        payment: Payment,
        *,
        raw_payload: dict,
    ):

        payment.status = PaymentStatus.REVERSED
        payment.raw_payload = raw_payload

        db.commit()
        db.refresh(payment)

        return payment

    @staticmethod
    def get_all(
        db: Session,
    ):

        return (
            db.query(Payment)
            .order_by(
                Payment.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        payment_id: UUID,
    ):

        return (
            db.query(Payment)
            .filter(
                Payment.id == payment_id
            )
            .first()
        )

    @staticmethod
    def get_student_payments(
        db: Session,
        student_id: UUID,
    ):

        return (
            db.query(Payment)
            .filter(
                Payment.student_id == student_id
            )
            .order_by(
                Payment.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_invoice_payments(
        db: Session,
        invoice_id: UUID,
    ):

        return (
            db.query(Payment)
            .filter(
                Payment.invoice_id == invoice_id
            )
            .order_by(
                Payment.created_at.desc()
            )
            .all()
        )