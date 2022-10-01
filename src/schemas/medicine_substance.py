import uuid
from typing import List

from pydantic import BaseModel, validator, Field


class MedicineSubstanceSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    medicine_id: uuid.UUID
    substance_id: uuid.UUID

    @validator("id", "medicine_id", "substance_id")
    def uuid_to_str(cls, value: uuid.UUID):
        if isinstance(value, uuid.UUID):
            return str(value)

    def __hash__(self):
        return hash((self.id, self.medicine_id, self.substance_id))

    class Config:
        orm_mode = True


class RelationsSchema(BaseModel):
    __root__: List[MedicineSubstanceSchema] = Field(alias="data")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True