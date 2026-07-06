from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.schemas.class_schema import ClassResponse
from app.services.class_service import ClassService

router = APIRouter(
    prefix="/classes",
    tags=["Classes"],
)


@router.get(
    "",
    response_model=list[ClassResponse],
    
)
def get_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return ClassService.get_all_classes(db)


@router.get(
    "/{class_id}",
    response_model=ClassResponse,
)
def get_class(
    class_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    class_obj = ClassService.get_class_by_id(db, class_id)

    if class_obj is None:
        raise HTTPException(
            status_code=404,
            detail="Class not found",
        )

    return class_obj