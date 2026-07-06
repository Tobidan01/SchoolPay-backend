from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.class_model import Class
from app.models.fee_structure import FeeStructure
from app.models.fee_structure_item import FeeStructureItem

from app.schemas import fee_structure
from app.schemas.fee_structure import (
    FeeStructureCreate,
    FeeStructureUpdate,
)


class FeeStructureService:

    @staticmethod
    def create(
        db: Session,
        payload: FeeStructureCreate,
    ):

        try:

            # Verify class exists
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

            # Prevent duplicates
            existing = (
                db.query(FeeStructure)
                .filter(
                    FeeStructure.class_id == payload.class_id,
                    FeeStructure.session == payload.session,
                    FeeStructure.term == payload.term,
                )
                .first()
            )

            if existing:
                raise ValueError(
                    "Fee structure already exists."
                )

            # Create fee structure
            fee_structure = FeeStructure(
                class_id=payload.class_id,
                session=payload.session,
                term=payload.term,
                title=payload.title,
            )

            db.add(fee_structure)

            db.flush()
            

            for item in payload.items:
                fee_item = FeeStructureItem(
                    title=item.title,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    amount=item.quantity * item.unit_price,
                )

                db.add(fee_item)
                db.commit()
                db.refresh(fee_structure)

                return fee_structure

        except Exception:

            db.rollback()

            raise

    @staticmethod
    def get_all(
        db: Session,
    ):
        return (
            db.query(FeeStructure)
            .all()
        )
    
    @staticmethod
    def get_by_id(
        db: Session,
        fee_structure_id,
    ):

        return (
            db.query(FeeStructure)
            .filter(
                FeeStructure.id == fee_structure_id
            )
            .first()
        )