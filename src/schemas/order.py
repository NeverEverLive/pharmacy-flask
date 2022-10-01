import uuid

from pydantic import BaseModel, validator


class OrderSchema(BaseModel):
    id: uuid.UUID
    recipe_id: uuid.UUID
    supplier_id: uuid.UUID
    check_id: uuid.UUID
    user_id: uuid.UUID
    name: str

    @validator("id", "recipe_id", "supplier_id", "check_id", "user_id")
    def uuid_to_str(cls, value: uuid.UUID):
        if isinstance(value, uuid.UUID):
            return str(value)

    def __hash__(self):
        return hash((self.id, self.recipe_id, self.supplier_id, self.check_id, self.user_id))

    class Config:
        orm_mode = True