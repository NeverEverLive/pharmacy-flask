from decimal import Decimal
from json import JSONEncoder
from datetime import date, timedelta, datetime
from pydantic import BaseModel
from uuid import UUID


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, (date, datetime, timedelta)):
                return str(obj)
            elif isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, BaseModel):
                return obj.dict(by_alias=True)
            elif isinstance(obj, UUID):
                return str(obj)
            elif isinstance(obj, Exception):
                return str(obj)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
