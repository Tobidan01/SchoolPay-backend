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
    nomba_signature: str | None = Header(None),
):

    raw_body = await request.body()

    if nomba_signature:
        NombaSignatureService.verify(
            raw_body,
            nomba_signature,
    )

    payment = PaymentWebhookService.process(
        db,
        payload,
    )

    return {
        "success": True,
        "payment_id": payment.id,
    }