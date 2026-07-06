from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Header,
    Request,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.webhook import NombaWebhookPayload
from app.services.nomba_signature_service import NombaSignatureService
from app.services.payment_webhook_service import PaymentWebhookService


router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)



@router.post("/nomba")
async def nomba_webhook(
    request: Request,
    payload: NombaWebhookPayload,
    db: Session = Depends(get_db),
    nomba_signature: Optional[str] = Header(default=None),
    nomba_timestamp: Optional[str] = Header(default=None),
):
        NombaSignatureService.verify(
            payload=payload,
            signature=nomba_signature,
            timestamp=nomba_timestamp,
    )

        result = PaymentWebhookService.process(
            db,
            payload,
    )

        return {
            "success": True,
            "duplicate": result["duplicate"],
            "payment_id": result["payment"].id,
    }