import base64
import hashlib
import hmac
import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.webhook import NombaWebhookPayload


logger = logging.getLogger(__name__)


class NombaSignatureService:
    """
    Generates and verifies Nomba webhook signatures.

    Signature algorithm:
    - HMAC SHA-256
    - Base64 encoded

    Signed value format:

    event_type:requestId:userId:walletId:transactionId:
    transaction_type:transaction_time:response_code:timestamp
    """

    @staticmethod
    def _format_time(
        value: datetime | str | None,
    ) -> str:
        """
        Normalize transaction time to UTC ISO-8601
        using the Z suffix.
        """

        if value is None:
            return ""

        if isinstance(value, str):
            return value.replace("+00:00", "Z")

        if value.tzinfo is None:
            value = value.replace(
                tzinfo=timezone.utc
            )

        return (
            value.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

    @staticmethod
    def _build_hashing_payload(
        payload: NombaWebhookPayload,
        timestamp: str,
    ) -> str:
        """
        Build the exact text that is signed.
        """

        transaction = payload.data.transaction
        merchant = payload.data.merchant

        response_code = (
            transaction.responseCode or ""
        )

        transaction_type = (
            transaction.type or ""
        )

        transaction_time = (
            NombaSignatureService._format_time(
                transaction.time
            )
        )

        return (
            f"{payload.event_type}:"
            f"{payload.requestId}:"
            f"{merchant.userId}:"
            f"{merchant.walletId}:"
            f"{transaction.transactionId}:"
            f"{transaction_type}:"
            f"{transaction_time}:"
            f"{response_code}:"
            f"{timestamp}"
        )

    @staticmethod
    def generate_signature(
        payload: NombaWebhookPayload,
        timestamp: str,
    ) -> str:
        """
        Generate a signature.

        Use this for local/Postman testing.
        In production, Nomba generates the signature.
        """

        webhook_secret = (
            settings.NOMBA_WEBHOOK_SECRET
        )

        if not webhook_secret:
            logger.error(
                "NOMBA_WEBHOOK_SECRET is not configured."
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Webhook signing key is not configured."
                ),
            )

        hashing_payload = (
            NombaSignatureService
            ._build_hashing_payload(
                payload=payload,
                timestamp=timestamp,
            )
        )

        digest = hmac.new(
            key=webhook_secret.encode("utf-8"),
            msg=hashing_payload.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()

        return base64.b64encode(
            digest
        ).decode("utf-8")

    @staticmethod
    def verify(
        payload: NombaWebhookPayload,
        signature: str | None,
        timestamp: str | None,
    ) -> bool:
        """
        Verify the signature received in a webhook request.
        """

        if not signature:
            raise HTTPException(
                status_code=(
                    status.HTTP_401_UNAUTHORIZED
                ),
                detail="Missing webhook signature.",
            )

        if not timestamp:
            raise HTTPException(
                status_code=(
                    status.HTTP_401_UNAUTHORIZED
                ),
                detail="Missing webhook timestamp.",
            )

        expected_signature = (
            NombaSignatureService.generate_signature(
                payload=payload,
                timestamp=timestamp,
            )
        )

        if not hmac.compare_digest(
            expected_signature.strip(),
            signature.strip(),
        ):
            logger.warning(
                "Invalid Nomba webhook signature. "
                "Request ID: %s; Transaction ID: %s",
                payload.requestId,
                payload.data.transaction.transactionId,
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_401_UNAUTHORIZED
                ),
                detail="Invalid webhook signature.",
            )

        logger.info(
            "Nomba webhook signature verified. "
            "Request ID: %s; Transaction ID: %s",
            payload.requestId,
            payload.data.transaction.transactionId,
        )

        return True