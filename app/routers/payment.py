from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.schemas.payment_schema import PaymentDashboardPageResponse, PaymentResponse
from app.services.payment_service import PaymentService

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)   



@router.get(
    "",
    response_model=PaymentDashboardPageResponse,
)
def get_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_admin
    ),
):
    return PaymentService.get_dashboard_page(
        db
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):

    payment = PaymentService.get_by_id(
        db,
        payment_id,
    )

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found.",
        )

    return payment


@router.get(
    "/student/{student_id}",
    response_model=list[PaymentResponse],
)
def get_student_payments(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return PaymentService.get_student_payments(
        db,
        student_id,
    )


@router.get(
    "/invoice/{invoice_id}",
    response_model=list[PaymentResponse],
)
def get_invoice_payments(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return PaymentService.get_invoice_payments(
        db,
        invoice_id,
    )