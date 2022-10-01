import uuid
from typing import List

from pydantic import BaseModel, validator, Field


class DoctorSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    first_name: str
    last_name: str
    hospital: str

    @validator("id")
    def uuid_to_str(cls, value: uuid.UUID):
        if isinstance(value, uuid.UUID):
            return str(value)

    def __hash__(self):
        return hash((self.id, self.first_name, self.last_name, self.hospital))

    class Config:
        orm_mode = True


class DoctorsSchema(BaseModel):
    __root__: List[DoctorSchema] = Field(alias="data")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
