from uuid import uuid4
from app.models.class_model import Class
from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base



class Student(Base):
    __tablename__ = "students"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    class_id = Column(
        UUID(as_uuid=True),
        ForeignKey("classes.id"),
        nullable=False,
    )

    admission_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    first_name = Column(
        String(100),
        nullable=False,
    )

    last_name = Column(
        String(100),
        nullable=False,
    )

    middle_name = Column(
        String(100),
        nullable=True,
    )

    email = Column(
        String(255),
        unique=True,
        nullable=True,
    )

    phone = Column(
        String(20),
        nullable=True,
    )

    gender = Column(
        String(20),
        nullable=False,
    )

    date_of_birth = Column(
        Date,
        nullable=True,
    )

    parent_name = Column(
        String(255),
        nullable=False,
    )

    parent_email = Column(
        String(255),
        nullable=True,
    )

    parent_phone = Column(
        String(20),
        nullable=False,
    )

    photo_url = Column(
        String(500),
        nullable=True,
    )

    photo_public_id = Column(
        String(255),
        nullable=True,
)
    status = Column(
        String(20),
        nullable=False,
        default="ACTIVE",
    )

    

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    

    school_class = relationship(
        "Class",
        back_populates="students",
    )

    virtual_account = relationship(
        "VirtualAccount",
        back_populates="student",
        uselist=False,
    )

    invoices = relationship(
        "Invoice",
        back_populates="student",
    )

    payments = relationship(
        "Payment",
        back_populates="student",
    )
    
    
    credits = relationship(
        "StudentCredit",
        back_populates="student",
        cascade="all, delete-orphan",
)
    
    credit = relationship(
        "StudentCredit",
        back_populates="student",
        uselist=False,
)
