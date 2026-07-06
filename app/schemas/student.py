from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr
from enum import Enum

from app.schemas.virtual_account import VirtualAccountResponse
from app.schemas.class_schema import ClassSummary

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class StudentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    GRADUATED = "GRADUATED"
    SUSPENDED = "SUSPENDED"
    WITHDRAWN = "WITHDRAWN"

class StudentCreate(BaseModel):
    class_id: UUID

    first_name: str
    last_name: str
    middle_name: str | None = None

    gender: Gender
    date_of_birth: date | None = None

    email: EmailStr | None = None
    phone: str | None = None

    parent_name: str
    parent_email: EmailStr | None = None
    parent_phone: str
    
    


class StudentUpdate(BaseModel):
    class_id: UUID | None = None

    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None

    gender: Gender | None = None
    date_of_birth: date | None = None

    email: EmailStr | None = None
    phone: str | None = None

    parent_name: str | None = None
    parent_email: EmailStr | None = None
    parent_phone: str | None = None

    status: StudentStatus | None = None

class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    class_id: UUID

    admission_number: str

    first_name: str
    last_name: str
    middle_name: str | None

    gender: Gender
    date_of_birth: date | None

    email: EmailStr | None
    phone: str | None

    parent_name: str
    parent_email: EmailStr |None
    parent_phone: str

    status: StudentStatus


class StudentRegistrationResponse(BaseModel):

    message: str

    student: StudentResponse

    virtual_account: VirtualAccountResponse

class StudentStatusUpdate(BaseModel):
    status: StudentStatus    


class StudentInvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    admission_number: str

    first_name: str
    last_name: str
    middle_name: str | None

    class_id: UUID  

class StudentSummary(BaseModel):
    id: UUID
    admission_number: str
    first_name: str
    last_name: str
    middle_name: str | None

    student_class:  ClassSummary    

    model_config = ConfigDict(from_attributes=True)                 