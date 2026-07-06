import uuid
from decimal import Decimal

from sqlalchemy.orm import Session
from app.models.payment import (
    Payment,
    PaymentStatus,
    PaymentProvider,
    PaymentMethod,
)
from app.models.invoice import Invoice
from app.models.virtual_account import VirtualAccount
from app.schemas import invoice, virtual_account
from app.schemas import invoice
from app.schemas.webhook import NombaWebhookPayload
from app.services.student_credit_service import StudentCreditService

class PaymentWebhookService:

    @staticmethod
    def process(
        db: Session,
        payload: NombaWebhookPayload,
    ):

        transaction = payload.data.transaction

        virtual_account = (
            db.query(VirtualAccount)
            .filter(
                VirtualAccount.account_number
                == payload.data.transaction.aliasAccountNumber
        )
        .first()
    )
        

        if not virtual_account:
            raise ValueError(
                "Virtual account not found."
            )

        existing_payment = (
            db.query(Payment)
            .filter(
                Payment.provider_transaction_id
                == transaction.transactionId
            )
            .first()
        )

        if existing_payment:
            return existing_payment


        query = (
            db.query(Invoice)
            .filter(
                Invoice.student_id == virtual_account.student_id,
                Invoice.balance > 0,
            )
    )

        print("Invoices found:", query.all())

        invoice = (
            query.order_by(
                Invoice.created_at.asc()
        )
        .first()
    )

        if not invoice:
            raise ValueError(
                "No unpaid invoice found."
            )

        amount = Decimal(
            str(transaction.transactionAmount)
        )

        payment = Payment(
             student_id=virtual_account.student_id,
            invoice_id=invoice.id,
            virtual_account_id=virtual_account.id,
            internal_reference=str(uuid.uuid4()),
            provider_transaction_id=transaction.transactionId,
            provider_session_id=transaction.sessionId,
            amount=amount,
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

            db.add(payment)

            received_amount = amount
            outstanding_balance = invoice.balance

            applied_amount = min(
                received_amount,
                outstanding_balance,
            )

            credit_amount = received_amount - applied_amount

            invoice.amount_paid += applied_amount
            invoice.balance -= applied_amount


            if invoice.balance <= 0:
                invoice.balance = Decimal("0")
                invoice.status = "PAID"
            else:
                invoice.status = "PARTIALLY_PAID"
    

            if credit_amount > 0:

                StudentCreditService.create(
                    db=db,
                    student_id=virtual_account.student_id,
                    payment_id=payment.id,
                    amount=credit_amount,
                )
            
            db.commit()
            db.refresh(payment)

            
            return payment      

        except Exception:
            db.rollback()
            raise