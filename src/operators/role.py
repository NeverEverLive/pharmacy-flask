import uuid

from src.schemas.role import RoleSchema, RolesSchema
from src.schemas.response import ResponseSchema
from src.models.role import Role
from src.models.base_model import get_session
from src.models.logger import Logger


def create_role(role: RoleSchema) -> ResponseSchema:
    role_state = Role().fill(**role.dict())

    with get_session() as session:
        session.add(role_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "role",
            "action": "delete",
            "object_info": RoleSchema.from_orm(role_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=RoleSchema.from_orm(role_state),
            message="Role created successfully",
            success=True
        )


def get_all_roles() -> ResponseSchema:
    with get_session() as session:
        roles_state = session.query(Role).order_by(Role.created_on.desc()).all()

        data = RolesSchema.from_orm(roles_state).dict(by_alias=True)["data"]

        return ResponseSchema(
            data=data,
            success=True
        )


def get_role(id: str) -> ResponseSchema:
    with get_session() as session:
        role_state = session.query(Role).filter_by(id=id).first()

        if not role_state:
            return ResponseSchema(
                success=False,
                message="Same role doesn't exist"
            )

        return ResponseSchema(
            data=RoleSchema.from_orm(role_state),
            success=True
        )


def update_role(role: RoleSchema) -> ResponseSchema:
    with get_session() as session:
        role_state = session.query(Role).filter_by(id=role.id).first()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "role",
            "action": "update",
            "object_info": RoleSchema.from_orm(role_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        role_state.name = role.name

        session.commit()

        return ResponseSchema(
            data=RoleSchema.from_orm(role_state),
            message="Role updated",
            success=True
        )


def delete_role(id: int) -> ResponseSchema:
    with get_session() as session:
        role_state = session.query(Role).filter_by(id=id).first()

        if not role_state:
            return ResponseSchema(
                success=False,
                message="Same role doesn't exist"
            )

        session.delete(role_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "role",
            "action": "insert",
            "object_info": RoleSchema.from_orm(role_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=RoleSchema.from_orm(role_state),
            message="Role deleted",
            success=True
        )
