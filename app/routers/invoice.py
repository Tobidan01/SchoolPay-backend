from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceDashboardPageResponse,
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
    status_code=status.HTTP_201_CREATED,
)
def create_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return InvoiceService.generate_invoice(
        db=db,
        payload=payload,
    )


@router.get(
    "",
    response_model=InvoiceDashboardPageResponse,
)
def get_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return InvoiceService.get_dashboard_page(db)


@router.get(
    "/student/{student_id}",
    response_model=list[InvoiceResponse],
)
def get_student_invoices(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return InvoiceService.get_student_invoices(
        db=db,
        student_id=student_id,
    )


@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
)
def get_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return InvoiceService.get_by_id(
        db=db,
        invoice_id=invoice_id,
    )