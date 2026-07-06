from uuid import UUID

from pydantic import BaseModel, ConfigDict
from enum import Enum


class VirtualAccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"

class VirtualAccountCreate(BaseModel):
    student_id: UUID

    account_number: str
    account_name: str
    bank_name: str

    provider: str = "NOMBA"
    provider_reference: str | None = None

    status: VirtualAccountStatus = VirtualAccountStatus.ACTIVE    


class VirtualAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID

    account_number: str
    account_name: str
    bank_name: str

    provider: str
    provider_reference: str | None

    status: VirtualAccountStatus
    is_active: bool