import base64
import hashlib
import hmac

from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.webhook import NombaWebhookPayload


class NombaSignatureService:
    """
    Verifies that a webhook request genuinely originated from Nomba.

    Signature Algorithm:
    - HMAC SHA256
    - Base64 Encoded
    """

    @staticmethod
    def verify(
        payload: NombaWebhookPayload,
        signature: str,
        timestamp: str,
    ) -> bool:

        if not signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing webhook signature.",
            )

        if not timestamp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing webhook timestamp.",
            )

        transaction = payload.data.transaction
        merchant = payload.data.merchant

        response_code = transaction.responseCode or ""

        hashing_payload = (
            f"{payload.event_type}:"
            f"{payload.requestId}:"
            f"{merchant.userId}:"
            f"{merchant.walletId}:"
            f"{transaction.transactionId}:"
            f"{transaction.type or ''}:"
            f"{transaction.time.isoformat().replace('+00:00', 'Z')}:"
            f"{response_code}:"
            f"{timestamp}"
        )

        expected_signature = base64.b64encode(
            hmac.new(
                key=settings.NOMBA_WEBHOOK_SECRET.encode("utf-8"),
                msg=hashing_payload.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).digest()
        ).decode("utf-8")

        if not hmac.compare_digest(
            expected_signature.strip(),
            signature.strip(),
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature.",
            )

        return True