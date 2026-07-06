from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel


class MerchantData(BaseModel):
    walletId: str
    walletBalance: Decimal
    userId: str


class TransactionData(BaseModel):
    aliasAccountNumber: str
    aliasAccountName: str | None = None
    aliasAccountReference: str | None = None
    aliasAccountType: str | None = None

    transactionId: str
    sessionId: str | None = None

    transactionAmount: Decimal

    narration: str | None = None

    fee: Decimal | None = None

    type: str | None = None

    originatingFrom: str | None = None

    responseCode: str | None = None

    time: datetime


class CustomerData(BaseModel):
    bankCode: str | None = None
    bankName: str | None = None
    senderName: str | None = None
    accountNumber: str | None = None


class WebhookPayloadData(BaseModel):
    merchant: MerchantData
    terminal: dict[str, Any] = {}
    transaction: TransactionData
    customer: CustomerData


class NombaWebhookPayload(BaseModel):
    event_type: str
    requestId: str
    data: WebhookPayloadData