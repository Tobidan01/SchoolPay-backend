from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceGenerateResponse,
    InvoiceResponse,
)
from app.services.invoice_service import InvoiceService

router = APIRouter(
    prefix="/invoices", 
    tags=["Invoices"],
)

@router.post(
    "/generate",
    response_model=InvoiceGenerateResponse,
    status_code=201,
)
def create_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    try:
        return InvoiceService.generate_invoice(
            db,
            payload,
)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.get(
    "",
    response_model=list[InvoiceResponse],
)
def get_all_invoices(
    db: Session = Depends(get_db),
):
    return InvoiceService.get_all(db)


@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
)
def get_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        return InvoiceService.get_by_id(
            db,
            invoice_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@router.get(
    "/student/{student_id}",
    response_model=list[InvoiceResponse],
)
def get_student_invoices(
    student_id: UUID,
    db: Session = Depends(get_db),
):
    return InvoiceService.get_student_invoices(
        db,
        student_id,
    )