from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from enum import Enum
from sqlalchemy import Enum as SQLEnum

class UserRole(str, Enum):
    ADMIN = "ADMIN"




class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.ADMIN)
    is_active = Column(Boolean, default=True)

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