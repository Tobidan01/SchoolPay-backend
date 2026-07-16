from datetime import date
from uuid import UUID
from fastapi import Form
from fastapi import UploadFile
from fastapi.params import File
from pydantic import BaseModel, ConfigDict, EmailStr
from enum import Enum
from typing import Annotated
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
    

    @classmethod
    def as_form(
        cls,
        class_id: Annotated[UUID, Form(...)],
        first_name: Annotated[str, Form(...)],
        last_name: Annotated[str, Form(...)],
        gender: Annotated[Gender, Form(...)],
        parent_name: Annotated[str, Form(...)],
        parent_phone: Annotated[str, Form(...)],

        middle_name: Annotated[str | None, Form()] = None,
        date_of_birth: Annotated[date | None, Form()] = None,
        email: Annotated[EmailStr | None, Form()] = None,
        phone: Annotated[str | None, Form()] = None,
        parent_email: Annotated[EmailStr | None, Form()] = None,
    ):
        return cls(
            class_id=class_id,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            gender=gender,
            date_of_birth=date_of_birth,
            email=email,
            phone=phone,
            parent_name=parent_name,
            parent_email=parent_email,
            parent_phone=parent_phone,
        )
    
    


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
    photo_url: str | None
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

    school_class:  ClassSummary    

    model_config = ConfigDict(from_attributes=True)                 