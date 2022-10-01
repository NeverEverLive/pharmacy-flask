import uuid
import datetime
from typing import List

from pydantic import BaseModel, validator, Field


class RecipeSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    doctor_id: uuid.UUID
    medicine_id: uuid.UUID
    electronic_signature: str
    created_on: datetime.date

    @validator("id", "doctor_id", "medicine_id", "user_id")
    def uuid_to_str(cls, value: uuid.UUID):
        if isinstance(value, uuid.UUID):
            return str(value)

    @validator('created_on')
    def data_formatter(cls, value: str):
        if isinstance(value, str):
            value = datetime.datetime.strptime(value, '%d-%m-%Y')
        return str(value)


    def __hash__(self):
        return hash((self.id, self.doctor_id, self.medicine_id, self.electronic_signature, self.created_on))

    class Config:
        orm_mode = True


class RecipesSchema(BaseModel):
    __root__: List[RecipeSchema] = Field(alias="data")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True