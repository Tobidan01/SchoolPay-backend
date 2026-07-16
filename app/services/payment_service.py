from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload

from app.models.invoice import Invoice
from app.models.payment import (
    Payment,
    PaymentMethod,
    PaymentProvider,
    PaymentStatus,
)
from app.models.student import Student
from app.schemas.payment_schema import PaymentDashboardItem, PaymentDashboardPageResponse, PaymentDashboardSummary


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
    def get_dashboard_page(
        db: Session,
    ) -> PaymentDashboardPageResponse:

        payments = (
            db.query(Payment)
            .options(
                joinedload(Payment.student)
                .joinedload(Student.school_class),

                joinedload(Payment.virtual_account),

                joinedload(Payment.invoice),
            )
            .order_by(
                Payment.created_at.desc()
            )
            .all()
        )

        payment_rows: list[
            PaymentDashboardItem
        ] = []

        todays_payments = 0
        revenue_today = Decimal("0")
        pending_payments = 0
        underpaid_payments = 0

        today = datetime.now(timezone.utc).date()

        for payment in payments:
            student = payment.student
            invoice = payment.invoice
            virtual_account = payment.virtual_account

            amount = Decimal(
                str(payment.amount or 0)
            )

            payment_status_value = (
                payment.status.value
                if hasattr(payment.status, "value")
                else str(payment.status)
            )

            # -----------------------------------
            # Dashboard status
            # -----------------------------------

            if payment_status_value == "PENDING":
                dashboard_status = "PENDING"
                pending_payments += 1

            elif payment_status_value == "FAILED":
                dashboard_status = "FAILED"

            elif payment_status_value == "REVERSED":
                dashboard_status = "REVERSED"

            elif payment_status_value == "SUCCESS":

                if invoice is None:
                    dashboard_status = "PAID"

                else:
                    invoice_status_value = (
                        invoice.status.value
                        if hasattr(
                            invoice.status,
                            "value",
                        )
                        else str(invoice.status)
                    )

                    if (
                        invoice_status_value
                        == "PARTIALLY_PAID"
                    ):
                        dashboard_status = (
                            "UNDERPAID"
                        )
                        underpaid_payments += 1

                    elif (
                        invoice_status_value
                        == "OVERPAID"
                    ):
                        dashboard_status = (
                            "OVERPAID"
                        )

                    else:
                        dashboard_status = "PAID"

            else:
                dashboard_status = (
                    payment_status_value
                )

            # -----------------------------------
            # Today's summary
            # -----------------------------------

            payment_date = (
                payment.paid_at
                or payment.created_at
            )

            if (
                payment_date is not None
                and payment_date.date() == today
            ):
                todays_payments += 1

                if (
                    payment_status_value
                    == "SUCCESS"
                ):
                    revenue_today += amount

            # -----------------------------------
            # Student fields
            # -----------------------------------

            if student is not None:
                full_name = " ".join(
                    part
                    for part in [
                        student.first_name,
                        student.middle_name,
                        student.last_name,
                    ]
                    if part
                )

                class_name = (
                    student.school_class.name
                    if student.school_class
                    else None
                )

                photo_url = student.photo_url
                student_id = student.id

            else:
                full_name = "Unknown Student"
                class_name = None
                photo_url = None
                student_id = payment.student_id

            # -----------------------------------
            # Other row values
            # -----------------------------------

            transaction_reference = (
                payment.provider_transaction_id
                or payment.internal_reference
            )

            payment_method = (
                payment.payment_method.value
                if hasattr(
                    payment.payment_method,
                    "value",
                )
                else str(payment.payment_method)
            )

            bank_name = (
                payment.payer_bank
                or "Unknown Bank"
            )

            account_number = (
                virtual_account.account_number
                if virtual_account
                else None
            )

            payment_rows.append(
                PaymentDashboardItem(
                    id=payment.id,
                    student_id=student_id,

                    full_name=full_name,
                    class_name=class_name,
                    photo_url=photo_url,

                    transaction_reference=(
                        transaction_reference
                    ),

                    amount=amount,

                    bank_name=bank_name,
                    payment_method=payment_method,

                    paid_at=payment_date,

                    account_number=(
                        account_number
                    ),

                    status=dashboard_status,
                )
            )

        summary = PaymentDashboardSummary(
            todays_payments=todays_payments,
            revenue_today=revenue_today,
            pending_payments=pending_payments,
            underpaid_payments=(
                underpaid_payments
            ),
        )

        return  PaymentDashboardPageResponse(
            summary=summary,
            payments=payment_rows,
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