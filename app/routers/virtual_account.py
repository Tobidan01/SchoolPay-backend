from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.schemas.virtual_account import (
    VirtualAccountResponse,
)
from app.services.virtual_account_service import (
    VirtualAccountService,
)

router = APIRouter(
    prefix="/virtual-accounts",
    tags=["Virtual Accounts"],
)



@router.get(
    "/student/{student_id}",
    response_model=VirtualAccountResponse,
)
def get_student_virtual_account(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    account = (
        VirtualAccountService.get_by_student_id(
            db,
            student_id,
        )
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Virtual account not found",
        )

    return account


@router.get(
    "/{virtual_account_id}",
    response_model=VirtualAccountResponse,
)
def get_virtual_account(
    virtual_account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin) 
):
    account = VirtualAccountService.get_by_id(
        db,
        virtual_account_id,
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Virtual account not found",
        )

    return account

@router.get(
    "",
    response_model=list[VirtualAccountResponse],
)
def get_virtual_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return VirtualAccountService.get_all(db)

