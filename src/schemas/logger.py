from typing import List
import datetime
import uuid
from pydantic import BaseModel, Field


class LoggerRequestSchema(BaseModel):
    limit: int


class LoggerSchema(BaseModel):
    id: uuid.UUID = Field(default=uuid.uuid4())
    table: str
    action: str
    object_info: dict
    executed: bool = Field(default=False)
    inserted_at: datetime.datetime

    class Config:
        orm_mode = True


class LoggerListSchema(BaseModel):
    __root__: List[LoggerSchema] = Field(alias="data")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True