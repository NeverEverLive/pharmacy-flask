import uuid
from typing import List

from pydantic import BaseModel, validator, Field


class SupplierSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str

    @validator("id")
    def uuid_to_str(cls, value: uuid.UUID):
        if isinstance(value, uuid.UUID):
            return str(value)

    def __hash__(self):
        return hash((self.id, self.name))

    class Config:
        orm_mode = True


class SuppliersSchema(BaseModel):
    __root__: List[SupplierSchema] = Field(alias="data")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
