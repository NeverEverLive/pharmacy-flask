import uuid
from typing import List

from pydantic import BaseModel, validator, Field


class OrderSchema(BaseModel):
    id: uuid.UUID = Field(default=uuid.uuid4())
    recipes_id: List[uuid.UUID]
    supplier_id: uuid.UUID
    check_id: uuid.UUID
    user_id: uuid.UUID
    name: str

    @validator("recipes_id")
    def list_uuid_to_str(cls, values: List[uuid.UUID]):
        str_id = []
        if isinstance(values, list):
            for value in values:
                str_id.append(str(value))
        return str_id

    @validator("id", "supplier_id", "check_id", "user_id")
    def uuid_to_str(cls, value: uuid.UUID):
        if isinstance(value, uuid.UUID):
            return str(value)        

    def __hash__(self):
        self.recipes_id = frozenset(self.recipes_id)
        return hash((self.id, self.recipes_id, self.supplier_id, self.check_id, self.user_id))

    class Config:
        orm_mode = True


class OrdersSchema(BaseModel):
    __root__: List[OrderSchema] = Field(alias="data")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
