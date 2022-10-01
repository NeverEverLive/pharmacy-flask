import uuid
import datetime

from pydantic import BaseModel, validator, Field


class CheckSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    date: datetime.date
    total_price: int
    
    @validator("id")
    def uuid_to_str(cls, value: uuid.UUID):
        if isinstance(value, uuid.UUID):
            return str(value)
    
    @validator('date')
    def data_formatter(cls, value: str):
        if isinstance(value, str):
            value = datetime.datetime.strptime(value, '%d-%m-%Y')
        return str(value)

    def __hash__(self):
        return hash((self.id, self.date, self.total_price))

    class Config:
        orm_mode = True