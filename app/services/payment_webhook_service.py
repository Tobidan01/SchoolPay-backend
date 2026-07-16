import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import (
    Payment,
    PaymentMethod,
    PaymentProvider,
    PaymentStatus,
)
from app.models.virtual_account import VirtualAccount
from app.schemas.webhook import NombaWebhookPayload
from app.services.student_credit_service import StudentCreditService


class PaymentWebhookService:

    @staticmethod
    def process(
        db: Session,
        payload: NombaWebhookPayload,
    ) -> dict:

        transaction = payload.data.transaction

        provider_transaction_id = (
            transaction.transactionId
        )

        amount_received = Decimal(
            str(transaction.transactionAmount)
        )

        if amount_received <= Decimal("0"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment amount must be greater than zero.",
            )

        # --------------------------------------------------
        # Duplicate webhook protection
        # --------------------------------------------------

        existing_payment = (
            db.query(Payment)
            .filter(
                Payment.provider_transaction_id
                == provider_transaction_id
            )
            .first()
        )

        if existing_payment is not None:
            return {
                "payment": existing_payment,
                "duplicate": True,
                "credit_created": Decimal("0"),
                "invoices_settled": 0,
            }

        try:
            # --------------------------------------------------
            # Find and lock virtual account
            # --------------------------------------------------

            virtual_account = (
                db.query(VirtualAccount)
                .filter(
                    VirtualAccount.account_number
                    == transaction.aliasAccountNumber
                )
                .with_for_update()
                .first()
            )

            if virtual_account is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Virtual account not found.",
                )

            # --------------------------------------------------
            # Lock all outstanding invoices
            # Oldest invoice gets paid first
            # --------------------------------------------------

            outstanding_invoices = (
                db.query(Invoice)
                .filter(
                    Invoice.student_id
                    == virtual_account.student_id,
                    Invoice.balance > Decimal("0"),
                )
                .order_by(
                    Invoice.created_at.asc()
                )
                .with_for_update()
                .all()
            )

            # The first invoice is stored as the payment's
            # primary invoice reference. It may be None when
            # the student has no outstanding invoices.
            primary_invoice = (
                outstanding_invoices[0]
                if outstanding_invoices
                else None
            )

            # --------------------------------------------------
            # Create payment
            # --------------------------------------------------

            payment = Payment(
                student_id=virtual_account.student_id,
                invoice_id=(
                    primary_invoice.id
                    if primary_invoice
                    else None
                ),
                virtual_account_id=virtual_account.id,

                internal_reference=str(uuid.uuid4()),

                provider_transaction_id=(
                    provider_transaction_id
                ),
                provider_session_id=(
                    transaction.sessionId
                ),

                amount=amount_received,
                currency="NGN",

                gateway_fee=(
                    Decimal(str(transaction.fee))
                    if transaction.fee is not None
                    else Decimal("0")
                ),

                provider=PaymentProvider.NOMBA,
                payment_method=PaymentMethod.TRANSFER,
                payment_channel=(
                    transaction.aliasAccountType
                    or "VIRTUAL_ACCOUNT"
                ),

                payer_name=(
                    payload.data.customer.senderName
                ),
                payer_bank=(
                    payload.data.customer.bankName
                ),
                payer_account_number=(
                    payload.data.customer.accountNumber
                ),

                narration=transaction.narration,
                status=PaymentStatus.SUCCESS,
                paid_at=transaction.time,

                raw_payload=payload.model_dump(
                    mode="json"
                ),
            )

            db.add(payment)
            db.flush()

            # --------------------------------------------------
            # Apply payment across outstanding invoices
            # --------------------------------------------------

            remaining_amount = amount_received
            invoices_settled = 0
            total_applied = Decimal("0")

            for invoice in outstanding_invoices:

                if remaining_amount <= Decimal("0"):
                    break

                invoice_balance = Decimal(
                    str(invoice.balance)
                )

                amount_to_apply = min(
                    remaining_amount,
                    invoice_balance,
                )

                invoice.amount_paid = (
                    Decimal(str(invoice.amount_paid))
                    + amount_to_apply
                )

                invoice.balance = (
                    invoice_balance - amount_to_apply
                )

                remaining_amount -= amount_to_apply
                total_applied += amount_to_apply

                if invoice.balance <= Decimal("0"):
                    invoice.balance = Decimal("0")
                    invoice.status = InvoiceStatus.PAID
                    invoices_settled += 1
                else:
                    invoice.status = (
                        InvoiceStatus.PARTIALLY_PAID
                    )

            # --------------------------------------------------
            # Remaining payment becomes student credit
            # --------------------------------------------------

            credit_created = Decimal("0")

            if remaining_amount > Decimal("0"):
                StudentCreditService.create(
                    db=db,
                    student_id=virtual_account.student_id,
                    payment_id=payment.id,
                    amount=remaining_amount,
                )

                credit_created = remaining_amount

            db.commit()
            db.refresh(payment)

            return {
                "payment": payment,
                "duplicate": False,
                "amount_received": amount_received,
                "amount_applied": total_applied,
                "credit_created": credit_created,
                "invoices_settled": invoices_settled,
            }

        except HTTPException:
            db.rollback()
            raise

        except IntegrityError:
            db.rollback()

            # Handles two webhook requests arriving
            # almost simultaneously.
            existing_payment = (
                db.query(Payment)
                .filter(
                    Payment.provider_transaction_id
                    == provider_transaction_id
                )
                .first()
            )

            if existing_payment:
                return {
                    "payment": existing_payment,
                    "duplicate": True,
                    "credit_created": Decimal("0"),
                    "invoices_settled": 0,
                }

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate payment transaction.",
            )

        except Exception as exc:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Payment processing failed: "
                    f"{str(exc)}"
                ),
            )