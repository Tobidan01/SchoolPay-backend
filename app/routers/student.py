from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.schemas.student import (
    StudentCreate,
    StudentRegistrationResponse,
    StudentResponse,
    StudentStatusUpdate,
    StudentUpdate,
)
from app.services.student_service import StudentService

router = APIRouter(
    prefix="/students",
    tags=["Students"],
)


@router.post(
    "",
    response_model=StudentRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)):
    return StudentService.create_student(
        db,
        payload,
    )


@router.get(
    "",
    response_model=list[StudentResponse],
)
def list_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return StudentService.get_students(db)


@router.get(
    "/{student_id}",
    response_model=StudentResponse,

)
def get_student(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    student = StudentService.get_student_by_id(
        db,
        student_id,
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    return student


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
)
def update_student(
    student_id: UUID,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    student = StudentService.update_student(
        db,
        student_id,
        payload,
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    return student


@router.patch("/{student_id}/status")
def update_student_status(
    student_id: UUID,
    payload: StudentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return StudentService.update_status(
        db,
        student_id,
        payload.status,
    )


@router.delete("/{student_id}")
def delete_student(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    deleted = StudentService.delete_student(
        db,
        student_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    return {
        "message": "Student deleted successfully"
    }