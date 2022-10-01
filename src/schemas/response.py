from typing import Any, List, Optional
from pydantic import BaseModel, root_validator, Field


SKIP_VALUES = {None}


class ResponseSchema(BaseModel):
    data: Optional[Any]
    success: bool
    message: Optional[str]

    @root_validator
    def remove_skip_values(cls, data):
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if isinstance(value, (dict, list)) and not []:
                    values = cls.remove_skip_values(value)
                    if any(values):
                        result.update({key: values})
                elif value not in SKIP_VALUES:
                    result.update({key: value})
        else:
            result = []
            for value in data:
                if isinstance(value, (dict, list)) and not []:
                    values = cls.remove_skip_values(value)
                    if any(values):
                        result.append(values)
                elif value not in SKIP_VALUES:
                    result.append(value)
        return result


class ManyResponseSchema(BaseModel):
    __root__: List[ResponseSchema] = Field(alias="data")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
