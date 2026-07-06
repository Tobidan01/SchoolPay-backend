import base64
import hashlib
import hmac

from fastapi import HTTPException

from app.core.config import settings


class NombaSignatureService:

    @staticmethod
    def verify(
        raw_body: bytes,
        signature: str,
    ) -> bool:

        expected_signature = base64.b64encode(
            hmac.new(
                settings.NOMBA_WEBHOOK_SECRET.encode(),
                raw_body,
                hashlib.sha256,
            ).digest()
        ).decode()

        if not hmac.compare_digest(
            expected_signature,
            signature,
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid webhook signature",
            )

        return True