from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.fee_structure import FeeStructure
from app.models.fee_structure_item import FeeStructureItem
from app.models.invoice import (
    Invoice,
    InvoiceStatus,
)
from app.models.invoice_item import InvoiceItem
from app.models.student import Student
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceDashboardItem,
    InvoiceDashboardPageResponse,
    InvoiceDashboardSummary,
)


class InvoiceService:

    @staticmethod
    def generate_invoice_number(
        db: Session,
    ) -> str:
        current_year = datetime.now().year

        count = (
            db.query(
                func.count(Invoice.id)
            )
            .filter(
                func.extract(
                    "year",
                    Invoice.created_at,
                )
                == current_year
            )
            .scalar()
        ) or 0

        next_number = count + 1

        return (
            f"INV-{current_year}-"
            f"{next_number:06d}"
        )

    @staticmethod
    def generate_invoice(
        db: Session,
        payload: InvoiceCreate,
    ):
        student = db.get(
            Student,
            payload.student_id,
        )

        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found.",
            )

        session_value = payload.session

        term_value = (
            payload.term.value
            if hasattr(payload.term, "value")
            else payload.term
        )

        existing_invoice = (
            db.query(Invoice)
            .filter(
                Invoice.student_id == student.id,
                Invoice.session == session_value,
                Invoice.term == term_value,
            )
            .first()
        )

        if existing_invoice is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Invoice already exists for this "
                    "student, session and term."
                ),
            )

        fee_structure = (
            db.query(FeeStructure)
            .options(
                joinedload(FeeStructure.items)
            )
            .filter(
                FeeStructure.class_id
                == student.class_id,
                FeeStructure.session
                == session_value,
                FeeStructure.term
                == term_value,
                FeeStructure.status
                == "ACTIVE",
            )
            .first()
        )

        if fee_structure is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "No active fee structure found "
                    "for the student's class, session "
                    "and term."
                ),
            )

        fee_items = fee_structure.items or []

        if not fee_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fee structure has no items.",
            )

        total = sum(
            (
                Decimal(str(item.quantity))
                * Decimal(str(item.unit_price))
                for item in fee_items
            ),
            Decimal("0"),
        )

        try:
            invoice = Invoice(
                student_id=student.id,
                invoice_number=(
                    InvoiceService
                    .generate_invoice_number(db)
                ),
                session=session_value,
                term=term_value,
                title=(
                    f"{term_value.replace('_', ' ').title()} "
                    "School Fees"
                ),
                description=(
                    f"{session_value} Academic "
                    "Session Fees"
                ),
                amount_due=total,
                amount_paid=Decimal("0"),
                balance=total,
                status=InvoiceStatus.UNPAID,
                due_date=payload.due_date,
            )

            db.add(invoice)
            db.flush()

            for item in fee_items:
                item_amount = (
                    Decimal(str(item.quantity))
                    * Decimal(str(item.unit_price))
                )

                invoice_item = InvoiceItem(
                    invoice_id=invoice.id,
                    fee_structure_item_id=item.id,
                    title=item.title,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    amount=item_amount,
                )

                db.add(invoice_item)

            db.commit()

            return (
                db.query(Invoice)
                .options(
                    joinedload(Invoice.student)
                    .joinedload(
                        Student.school_class
                    ),
                    joinedload(Invoice.items),
                )
                .filter(
                    Invoice.id == invoice.id
                )
                .first()
            )

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Invoice number conflict. "
                    "Please try again."
                ),
            )

        except HTTPException:
            db.rollback()
            raise

        except Exception as exc:
            db.rollback()

            raise HTTPException(
                status_code=(
                    status
                    .HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Invoice generation failed: "
                    f"{str(exc)}"
                ),
            )

    @staticmethod
    def get_dashboard_page(
        db: Session,
    ) -> InvoiceDashboardPageResponse:

        invoices = (
            db.query(Invoice)
            .options(
                joinedload(Invoice.student),
            )
            .order_by(
                Invoice.created_at.desc()
            )
            .all()
        )

        invoice_rows: list[
            InvoiceDashboardItem
        ] = []

        expected_revenue = Decimal("0")
        outstanding_balance = Decimal("0")
        paid_invoices = 0

        for invoice in invoices:
            student = invoice.student

            amount_due = Decimal(
                str(invoice.amount_due or 0)
            )

            amount_paid = Decimal(
                str(invoice.amount_paid or 0)
            )

            balance = Decimal(
                str(invoice.balance or 0)
            )

            database_status = (
                invoice.status.value
                if hasattr(invoice.status, "value")
                else str(invoice.status)
            )

            if database_status == "PAID":
                dashboard_status = "PAID"

            elif database_status == "OVERPAID":
                dashboard_status = "OVERPAID"

            elif database_status == "PARTIALLY_PAID":
                dashboard_status = "UNDERPAID"

            else:
                dashboard_status = "PENDING"

            if dashboard_status in {
                "PAID",
                "OVERPAID",
            }:
                paid_invoices += 1

            if student is not None:
                full_name = " ".join(
                    part
                    for part in [
                        student.first_name,
                        student.middle_name,
                        student.last_name,
                    ]
                    if part
                )

                student_id = student.id
                photo_url = student.photo_url

            else:
                full_name = "Unknown Student"
                student_id = invoice.student_id
                photo_url = None

            invoice_rows.append(
                InvoiceDashboardItem(
                    id=invoice.id,
                    student_id=student_id,
                    full_name=full_name,
                    photo_url=photo_url,
                    invoice_number=(
                        invoice.invoice_number
                    ),
                    fee_type=invoice.title,
                    amount=amount_due,
                    due_date=invoice.due_date,
                    amount_paid=amount_paid,
                    status=dashboard_status,
                )
            )

            expected_revenue += amount_due
            outstanding_balance += balance

        summary = InvoiceDashboardSummary(
            total_invoices=len(invoice_rows),
            expected_revenue=expected_revenue,
            outstanding_balance=(
                outstanding_balance
            ),
            paid_invoices=paid_invoices,
        )

        return InvoiceDashboardPageResponse(
            summary=summary,
            invoices=invoice_rows,
        )

    @staticmethod
    def get_by_id(
        db: Session,
        invoice_id: UUID,
    ) -> Invoice:

        invoice = (
            db.query(Invoice)
            .options(
                joinedload(Invoice.student)
                .joinedload(
                    Student.school_class
                ),
                joinedload(Invoice.items),
            )
            .filter(
                Invoice.id == invoice_id
            )
            .first()
        )

        if invoice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found.",
            )

        return invoice

    @staticmethod
    def get_student_invoices(
        db: Session,
        student_id: UUID,
    ) -> list[Invoice]:

        student = db.get(
            Student,
            student_id,
        )

        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found.",
            )

        return (
            db.query(Invoice)
            .options(
                joinedload(Invoice.student)
                .joinedload(
                    Student.school_class
                ),
                joinedload(Invoice.items),
            )
            .filter(
                Invoice.student_id
                == student_id
            )
            .order_by(
                Invoice.created_at.desc()
            )
            .all()
        )