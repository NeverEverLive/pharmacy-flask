import uuid

from src.schemas.check import CheckSchema
from src.schemas.response import ResponseSchema
from src.models.check import Check
from src.models.base_model import get_session
from src.models.logger import Logger


def create_check(check: CheckSchema) -> ResponseSchema:
    check_state = Check().fill(**check.dict())

    with get_session() as session:
        session.add(check_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "check",
            "action": "delete",
            "object_info": CheckSchema.from_orm(check_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=CheckSchema.from_orm(check_state),
            message="Check created successfuly",
            success=True
        )

def get_check(id: str) -> ResponseSchema:
    with get_session() as session:
        check_state = session.query(Check).filter_by(id=id).all()

        if not check_state:
            return ResponseSchema(
                data=[],
                success=False,
                message="Same check doesn't exist"
            )

        return ResponseSchema(
            data=CheckSchema.from_orm(check_state).dict(by_alias=True)["data"],
            success=True
        )