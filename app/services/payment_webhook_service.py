import uuid
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
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
    ):

        transaction = payload.data.transaction

        # --------------------------------------------------
        # Find Virtual Account
        # --------------------------------------------------

        virtual_account = (
            db.query(VirtualAccount)
            .filter(
                VirtualAccount.account_number
                == transaction.aliasAccountNumber
            )
            .first()
        )

        if virtual_account is None:
            raise HTTPException(
                status_code=404,
                detail="Virtual account not found.",
            )

        # --------------------------------------------------
        # Prevent Duplicate Processing
        # --------------------------------------------------

        existing_payment = (
            db.query(Payment)
            .filter(
                Payment.provider_transaction_id
                == transaction.transactionId
            )
            .first()
        )

        if existing_payment:
            return {
                "payment": existing_payment,
                "duplicate": True,
            }

        # --------------------------------------------------
        # Get Oldest Outstanding Invoice
        # --------------------------------------------------

        outstanding_invoice = (
            db.query(Invoice)
            .filter(
                Invoice.student_id == virtual_account.student_id,
                Invoice.balance > 0,
            )
            .order_by(
                Invoice.created_at.asc()
            )
            .first()
        )

        if outstanding_invoice is None:
            raise HTTPException(
                status_code=404,
                detail="No outstanding invoice.",
            )

        amount_received = Decimal(
            str(transaction.transactionAmount)
        )

        payment = Payment(
            student_id=virtual_account.student_id,
            invoice_id=outstanding_invoice.id,
            virtual_account_id=virtual_account.id,

            internal_reference=str(uuid.uuid4()),

            provider_transaction_id=transaction.transactionId,
            provider_session_id=transaction.sessionId,

            amount=amount_received,
            currency="NGN",

            gateway_fee=transaction.fee,

            provider=PaymentProvider.NOMBA,
            payment_method=PaymentMethod.TRANSFER,
            payment_channel=transaction.aliasAccountType,

            payer_name=payload.data.customer.senderName,
            payer_bank=payload.data.customer.bankName,
            payer_account_number=payload.data.customer.accountNumber,

            narration=transaction.narration,

            status=PaymentStatus.SUCCESS,

            paid_at=transaction.time,

            raw_payload=payload.model_dump(mode="json"),
        )

        try:

            # ----------------------------------------
            # Save Payment
            # ----------------------------------------

            db.add(payment)

            # Generate payment.id before creating credit
            db.flush()

            outstanding_balance = outstanding_invoice.balance

            applied_amount = min(
                amount_received,
                outstanding_balance,
            )

            credit_amount = amount_received - applied_amount

            # ----------------------------------------
            # Update Invoice
            # ----------------------------------------

            outstanding_invoice.amount_paid += applied_amount
            outstanding_invoice.balance -= applied_amount

            if outstanding_invoice.balance <= 0:
                outstanding_invoice.balance = Decimal("0")
                outstanding_invoice.status = "PAID"
            else:
                outstanding_invoice.status = "PARTIALLY_PAID"

            # ----------------------------------------
            # Create Student Credit
            # ----------------------------------------

            if credit_amount > 0:

                StudentCreditService.create(
                    db=db,
                    student_id=virtual_account.student_id,
                    payment_id=payment.id,
                    amount=credit_amount,
                )

            # ----------------------------------------
            # Commit Everything
            # ----------------------------------------

            db.commit()

            db.refresh(payment)

            return {
                "payment": payment,
                "duplicate": False,
            }

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Payment processing failed: {str(e)}",
            )