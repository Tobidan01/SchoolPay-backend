from fastapi.params import Depends
from sqlalchemy import UUID
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.virtual_account import VirtualAccount
from app.schemas.virtual_account import VirtualAccountResponse
from app.schemas.virtual_account import VirtualAccountResponse
from app.services.nomba_service import NombaService


class VirtualAccountService:
    @staticmethod
    def create_for_student(db: Session, student):

        response = NombaService.create_virtual_account(student)

        if response["code"] != "00":
            raise ValueError(response["description"])

        data = response["data"]

        account = VirtualAccount(
            student_id=student.id,
            account_number=data["bankAccountNumber"],
            account_name=data["bankAccountName"],
            bank_name=data["bankName"],
            provider="NOMBA",
            provider_reference=data["accountRef"],
            status="ACTIVE",
            is_active=True,
        )

        db.add(account)

        return account
    
    @staticmethod
    def get_by_id(
        db: Session,
        virtual_account_id: UUID,
    ):
        return (
            db.query(VirtualAccount)
            .filter(VirtualAccount.id == virtual_account_id)
            .first()
        )
    
    @staticmethod
    def get_all(db: Session):
        return (
            db.query(VirtualAccount)
            .all()
    )


    @staticmethod
    def get_by_student_id(
        db: Session,
        student_id: UUID,
):
        return (
            db.query(VirtualAccount)
            .filter(
                VirtualAccount.student_id == student_id
        )
        .first()
    )