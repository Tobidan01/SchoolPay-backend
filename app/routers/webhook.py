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
from app.services.nomba_signature_service import (
    NombaSignatureService,
)
from app.services.payment_webhook_service import (
    PaymentWebhookService,
)


router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


@router.post("/nomba")
async def nomba_webhook(
    request: Request,
    payload: NombaWebhookPayload,
    db: Session = Depends(get_db),
    nomba_signature: Optional[str] = Header(
        default=None
    ),
    nomba_timestamp: Optional[str] = Header(
        default=None
    ),
):
    NombaSignatureService.verify(
        payload=payload,
        signature=nomba_signature,
        timestamp=nomba_timestamp,
    )

    result = PaymentWebhookService.process(
        db=db,
        payload=payload,
    )

    payment = result["payment"]

    return {
        "success": True,
        "duplicate": result["duplicate"],
        "payment_id": str(payment.id),
        "amount_received": str(
            result.get("amount_received", payment.amount)
        ),
        "amount_applied": str(
            result.get("amount_applied", "0")
        ),
        "credit_created": str(
            result.get("credit_created", "0")
        ),
        "invoices_settled": result.get(
            "invoices_settled",
            0,
        ),
    }