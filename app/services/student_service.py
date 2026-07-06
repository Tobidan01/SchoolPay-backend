import re
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.class_model import Class
from app.models.student import Student
from app.schemas.student import (
    StudentCreate,
    StudentStatus,
    StudentUpdate,
)
from app.services.virtual_account_service import (
    VirtualAccountService,
)


class StudentService:


    @staticmethod
    def generate_admission_number(db: Session) -> str:
        """
        Generates the next admission number.

        Example:
        SP00001
        SP00002
        SP00003
        """

        last_student = (
            db.query(Student)
            .order_by(Student.admission_number.desc())
            .first()
        )

        if last_student is None:
            return "SP00001"

        match = re.search(
            r"(\d+)$",
            last_student.admission_number,
        )

        if match is None:
            raise ValueError(
                "Invalid admission number format."
            )

        next_number = int(match.group()) + 1

        return f"SP{next_number:05d}"

    
    @staticmethod
    def create_student(
        db: Session,
        payload: StudentCreate,
    ):
        try:

            # ===========================================
            # Verify class exists
            # ===========================================

            school_class = (
                db.query(Class)
                .filter(
                    Class.id == payload.class_id
                )
                .first()
            )

            if school_class is None:
                raise ValueError(
                    "Class not found."
                )

            # ===========================================
            # Email uniqueness
            # ===========================================

            if payload.email:

                existing_email = (
                    db.query(Student)
                    .filter(
                        Student.email == payload.email
                    )
                    .first()
                )

                if existing_email:
                    raise ValueError(
                        "Student email already exists."
                    )

            # ===========================================
            # Generate Admission Number
            # ===========================================

            admission_number = (
                StudentService.generate_admission_number(
                    db
                )
            )

            # ===========================================
            # Create Student
            # ===========================================

            student = Student(
                admission_number=admission_number,
                status=StudentStatus.ACTIVE,
                **payload.model_dump(),
            )

            db.add(student)

            # Generates UUID before commit
            db.flush()

            # ===========================================
            # Create Virtual Account
            # ===========================================

            virtual_account = (
                VirtualAccountService.create_for_student(
                    db=db,
                    student=student,
                )
            )

            # ===========================================
            # Commit Everything
            # ===========================================

            db.commit()

            db.refresh(student)
            db.refresh(virtual_account)

            # ===========================================
            # Response
            # ===========================================

            return {
                "message": "Student created successfully.",

                "student": student,

                "virtual_account": virtual_account,
            }

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_students(
        db: Session,
    ):
        return (
            db.query(Student)
            .all()
        )

    @staticmethod
    def get_student_by_id(
        db: Session,
        student_id: UUID,
    ):
        return (
            db.query(Student)
            .filter(
                Student.id == student_id
            )
            .first()
        )

    @staticmethod
    def update_student(
        db: Session,
        student_id: UUID,
        payload: StudentUpdate,
    ):

        student = (
            db.query(Student)
            .filter(
                Student.id == student_id
            )
            .first()
        )

        if student is None:
            return None

        updates = payload.model_dump(
            exclude_unset=True
        )

        for key, value in updates.items():
            setattr(
                student,
                key,
                value,
            )

        db.commit()
        db.refresh(student)

        return student
    
    @staticmethod
    def update_status(
        db: Session,
        student_id: UUID,
        status: StudentStatus,
    ):
        student = (
            db.query(Student)
            .filter(Student.id == student_id)
            .first()
        )

        if student is None:
            raise ValueError("Student not found.")

        student.status = status

        db.commit()

        db.refresh(student)

        return student

    @staticmethod
    def delete_student(
        db: Session,
        student_id: UUID,
    ):

        student = (
            db.query(Student)
            .filter(
                Student.id == student_id
            )
            .first()
        )

        if student is None:
            return False

        db.delete(student)
        db.commit()

        return True