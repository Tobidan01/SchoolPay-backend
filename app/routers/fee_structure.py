from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.fee_structure import FeeStructure
from app.models.user import User
from app.schemas.fee_structure import (
    FeeStructureCreate,
    FeeStructureResponse,
    FeeStructureUpdate,
)
from app.services.fee_structure_service import FeeStructureService

router = APIRouter(
    prefix="/fee-structures",
    tags=["Fee Structures"],
)


@router.post(
    "",
    response_model=FeeStructureResponse,
)
def create_fee_structure(
    payload: FeeStructureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return FeeStructureService.create(
        db,
        payload,
    )



@router.get(
    "",
    response_model=list[FeeStructureResponse],
)
def get_fee_structures(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return FeeStructureService.get_all(db)




@router.get(
    "/{fee_structure_id}",
    response_model=FeeStructureResponse,
)
def get_fee_structure(
    fee_structure_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    fee_structure = FeeStructureService.get_by_id(
        db,
        fee_structure_id,
    )

    if fee_structure is None:
        raise HTTPException(
            status_code=404,
            detail="Fee structure not found.",
        )

    return fee_structure


@router.patch(
    "/{fee_structure_id}",
    response_model=FeeStructureResponse,
)
def update_fee_structure(
    fee_structure_id: UUID,
    payload: FeeStructureUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return FeeStructureService.update(
        db,
        fee_structure_id,
        payload,
    )

@router.delete(
    "/{fee_structure_id}",
)
def delete_fee_structure(
    fee_structure_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    FeeStructureService.delete(
        db,
        fee_structure_id,
    )

    return {
        "message": "Fee structure deleted successfully."
    }

@staticmethod
def update(
    db: Session,
    fee_structure_id: UUID,
    payload: FeeStructureUpdate,
    current_user: User = Depends(get_current_admin)
):
    try:

        fee_structure = (
            db.query(FeeStructure)
            .filter(
                FeeStructure.id == fee_structure_id
            )
            .first()
        )

        if fee_structure is None:
            raise ValueError(
                "Fee structure not found."
            )

        updates = payload.model_dump(
            exclude_unset=True
        )

        for key, value in updates.items():
            setattr(
                fee_structure,
                key,
                value,
            )

        db.commit()

        db.refresh(
            fee_structure,
        )

        return fee_structure

    except Exception:
        db.rollback()
        raise


@staticmethod
def delete(
    db: Session,
    fee_structure_id: UUID,
):
    try:

        fee_structure = (
            db.query(FeeStructure)
            .filter(
                FeeStructure.id == fee_structure_id
            )
            .first()
        )

        if fee_structure is None:
            raise ValueError(
                "Fee structure not found."
            )

        db.delete(
            fee_structure
        )

        db.commit()

    except Exception:
        db.rollback()
        raise    