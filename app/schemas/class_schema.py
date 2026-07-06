from uuid import UUID

from pydantic import BaseModel, ConfigDict

class ClassSummary(BaseModel):
    id: UUID
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)

class ClassResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None