from enum import Enum
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.models.class_model import Class
from app.models.fee_structure import FeeStructure
from app.models.fee_structure_item import (
    FeeStructureItem,
)
from app.schemas.fee_structure import (
    FeeStructureCreate,
    FeeStructureUpdate,
)


class FeeStructureService:

    @staticmethod
    def create(
        db: Session,
        payload: FeeStructureCreate,
    ) -> FeeStructure:

        school_class = db.get(
            Class,
            payload.class_id,
        )

        if school_class is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found.",
            )

        existing = (
            db.query(FeeStructure)
            .filter(
                FeeStructure.class_id
                == payload.class_id,
                FeeStructure.session
                == payload.session,
                FeeStructure.term
                == payload.term.value,
            )
            .first()
        )

        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An active fee structure already "
                    "exists for this class, session, "
                    "and term."
                ),
            )

        try:
            fee_structure = FeeStructure(
                class_id=payload.class_id,
                session=payload.session,
                term=payload.term.value,
                title=payload.title,
                status="ACTIVE",
            )

            db.add(fee_structure)
            db.flush()

            for item in payload.items:
                fee_item = FeeStructureItem(
                    fee_structure_id=fee_structure.id,
                    title=item.title,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )

                db.add(fee_item)

            db.commit()

            return (
                db.query(FeeStructure)
                .options(
                    selectinload(
                        FeeStructure.items
                    )
                )
                .filter(
                    FeeStructure.id
                    == fee_structure.id
                )
                .first()
            )

        except HTTPException:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[FeeStructure]:

        return (
            db.query(FeeStructure)
            .options(
                selectinload(
                    FeeStructure.items
                )
            )
            .order_by(
                FeeStructure.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        fee_structure_id: UUID,
    ) -> FeeStructure | None:

        return (
            db.query(FeeStructure)
            .options(
                selectinload(
                    FeeStructure.items
                )
            )
            .filter(
                FeeStructure.id
                == fee_structure_id
            )
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        fee_structure_id: UUID,
        payload: FeeStructureUpdate,
    ) -> FeeStructure:

        fee_structure = db.get(
            FeeStructure,
            fee_structure_id,
        )

        if fee_structure is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fee structure not found.",
            )

        updates = payload.model_dump(
            exclude_unset=True
        )

        for key, value in updates.items():
            if isinstance(value, Enum):
                value = value.value

            setattr(
                fee_structure,
                key,
                value,
            )

        try:
            db.commit()
            db.refresh(fee_structure)

            return fee_structure

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete(
        db: Session,
        fee_structure_id: UUID,
    ) -> None:

        fee_structure = db.get(
            FeeStructure,
            fee_structure_id,
        )

        if fee_structure is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fee structure not found.",
            )

        try:
            db.delete(fee_structure)
            db.commit()

        except Exception:
            db.rollback()
            raise