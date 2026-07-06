from uuid import uuid4
from pydantic import BaseModel, BaseModel, ConfigDict
from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Class(Base):
    __tablename__ = "classes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)

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

    students = relationship(
        "Student",
        back_populates="school_class",
    )
    
    fee_structures = relationship(
        "FeeStructure",
        back_populates="school_class",
    )    

