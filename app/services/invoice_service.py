from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import invoice
from app.models import invoice_item
from app.models.student import Student
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.fee_structure import FeeStructure
from app.models.fee_structure_item import FeeStructureItem
from app.schemas import student
from app.schemas import invoice
from app.schemas.invoice import InvoiceCreate
from app.schemas.invoice import InvoiceStatus


class InvoiceService:



    @staticmethod
    def generate_invoice_number(db: Session) -> str:
        current_year = datetime.now().year

        count = (
            db.query( func.count(Invoice.id))
            .filter(
                func.extract("year", Invoice.created_at) == current_year
            )
            .scalar()
        )

        next_number = count + 1

        return f"INV-{current_year}-{next_number:06d}"

    @staticmethod
    def generate_invoice(
        db: Session,
        payload: InvoiceCreate,
    ):
        try:

            # ==============================================
            # Verify student exists
            # ==============================================
            student = (
                db.query(Student)
                .filter(
                    Student.id == payload.student_id
                )
                .first()
            )

            if student is None:
                raise ValueError(
                    "Student not found."
                )

            # ==============================================
            # Prevent duplicate invoice
            # ==============================================
            existing_invoice = (
                db.query(Invoice)
                .filter(
                    Invoice.student_id == student.id,
                    Invoice.session == payload.session,
                    Invoice.term == payload.term,
                )
                .first()
            )

            if existing_invoice:
                raise ValueError(
                    "Invoice already exists for this session and term."
                )

            # ==============================================
            # Find active fee structure
            # ==============================================
            fee_structure = (
                db.query(FeeStructure)
                .filter(
                    FeeStructure.class_id == student.class_id,
                    FeeStructure.session == payload.session,
                    FeeStructure.term == payload.term,
                    FeeStructure.status == "ACTIVE",
                )
                .first()
            )

            if fee_structure is None:
                raise ValueError(
                    "No active fee structure found."
                )

            # ==============================================
            # Load fee structure items
            # ==============================================
            fee_items = (
                db.query(FeeStructureItem)
                .filter(
                    FeeStructureItem.fee_structure_id
                    == fee_structure.id
                )
                .all()
            )

            if not fee_items:
                raise ValueError(
                    "Fee structure has no items."
                )

            # ==============================================
            # Calculate invoice total
            # ==============================================
            total = Decimal("0")

            for item in fee_items:
                total += item.quantity * item.unit_price

            # ==============================================
            # Create invoice
            # ==============================================
            invoice = Invoice(
                student_id=student.id,
                invoice_number=InvoiceService.generate_invoice_number(db),
                session=payload.session,
                term=payload.term,
                title=f"{payload.term} School Fees",
                description=f"{payload.session} Academic Session Fees",
                amount_due=total,
                amount_paid=Decimal("0"),
                balance=total,
                status=InvoiceStatus.UNPAID,
                due_date=payload.due_date,
            )

            db.add(invoice)

            db.flush()

            # ==============================================
            # Copy fee structure items
            # ==============================================
            for item in fee_items:

                invoice_item = InvoiceItem(
                    invoice_id=invoice.id,
                    fee_structure_item_id=item.id,
                    title=item.title,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    amount=item.quantity * item.unit_price,
                )

                db.add(invoice_item)

            # ==============================================
            # Commit
            # ==============================================
            db.commit()

            db.refresh(invoice)

            return {
                "message": "Invoice generated successfully.",
                "invoice": invoice,
                "student": student,
                "items": invoice.items,
            }

        except Exception:
            db.rollback()
            raise
    @staticmethod
    def get_all(
        db: Session,
    ):
        return db.query(Invoice).all()

    @staticmethod
    def get_by_id(
        db: Session,
        invoice_id: UUID,
    ):
        invoice = (
            db.query(Invoice)
            .options(
                joinedload(Invoice.student).joinedload(Student.student_class),
                joinedload(Invoice.items),
                
        )
        .filter(Invoice.id == invoice_id)
        .first()
    )

        if not invoice:
            raise ValueError("Invoice not found")

        return invoice
    
    @staticmethod
    def get_student_invoices(
        db: Session,
        student_id: UUID,
    ):
        return (
            db.query(Invoice)
            .filter(
                Invoice.student_id == student_id,
            )
            .all()
        )
