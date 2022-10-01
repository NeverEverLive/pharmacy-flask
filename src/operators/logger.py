import logging

from sqlalchemy.orm import Session

from src.schemas.logger import LoggerListSchema, LoggerSchema
from src.schemas.response import ResponseSchema
from src.models.base_model import get_session
from src.models.logger import Logger


def apply(limit: int):
    with get_session() as session:
        logger_state = session.query(Logger).filter(Logger.executed == False).order_by(Logger.inserted_at.desc()).limit(limit).all()

        for log in logger_state:
            if log.action == "delete":
                apply_delete(log, session)
                session.merge(log)
                session.commit()
            if log.action == "insert":
                apply_insert(log, session)
                session.merge(log)
                session.commit()
            if log.action == "update":
                apply_update(log, session)
                session.merge(log)
                session.commit()

        return ResponseSchema(
            data = LoggerListSchema.from_orm(logger_state).dict(by_alias=True)["data"],
            success=True
        )

def apply_delete(log: LoggerSchema, session: Session):
    query = f"DELETE FROM {log.table} WHERE id='{log.object_info['id']}'"
    session.execute(query)
    log.executed = True


def apply_insert(log: LoggerSchema, session: Session):
    values = "'" + "', '".join(map(str, log.object_info.values())) + "'"
    query = f"INSERT INTO {log.table}({', '.join(log.object_info.keys())}) values ({values})"
    session.execute(query)
    log.executed = True


def apply_update(log: LoggerSchema, session: Session):
    id = log.object_info.pop("id")
    values = "'" + "', '".join(map(str, log.object_info.values())) + "'"
    query = f"UPDATE {log.table} SET ({', '.join(log.object_info.keys())}) = ({values}) WHERE id='{id}'"
    session.execute(query)
    log.object_info["id"] = id
    log.executed = True
