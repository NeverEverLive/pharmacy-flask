import datetime
import uuid
from uuid import uuid4

from sqlalchemy import Column, func, PrimaryKeyConstraint, ForeignKeyConstraint, event, DDL
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import String, DateTime
from marshmallow import Schema, fields
from pydantic import Field, BaseModel as BaseSchema

from src.models.base_model import BaseModel, get_session
from src.models.role import Role
from src.schemas.user import UserSchema


class User(BaseModel):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid4())
    role_id = Column(UUID(as_uuid=True), nullable=False)
    username = Column(String, unique=True, nullable=False)
    hash_password = Column(String, nullable=False)
    created_on = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=datetime.datetime.now)
    
    order = relationship("Order", back_populates="user", uselist=True)
    role = relationship("Role", back_populates="user")

    __table_args__ = (
        PrimaryKeyConstraint(id),
        ForeignKeyConstraint(
            (
                role_id,
            ),
            (
                "role.id",
            )
        ),
    )

    def __repr__(self):
        return self.username

    @classmethod
    def get_by_id(cls, id):
        """Вернуть пользователя по id"""
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_by_username(cls, username):
        """Вернуть пользователя по username"""
        return cls.query.filter_by(username=username).first()


class LoginUserSchema(Schema):
    username = fields.String()
    password = fields.String()


class CreateUpdateUserSchema(Schema):
    id = fields.UUID(default=uuid4())
    username = fields.String()
    hash_password = fields.String()
    role_id = fields.UUID(defaut=uuid4())


class SaveUserSchema(BaseSchema):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    username: str
    role_id: uuid.UUID

    class Config:
        orm_mode = True


# def create_admin():
#     """DDL при создании таблицы добавляет пользователя admin"""
#     admin_user = {
#         # "id": uuid.uuid4(),
#         "username": "admin",
#         "password": "123"
#     }
#
#     with get_session() as session:
#         role_id = session.query(Role).first()
#
#     admin_user["role_id"] = role_id
#     serializing_data = UserSchema.parse_obj(admin_user)
#     return DDL(f"""INSERT INTO "user"(id, username, hash_password, role_id)
#                 VALUES
#                 ('{serializing_data.id}', '{serializing_data.username}', '{serializing_data.hash_password}', '{serializing_data.role_id}')
#                 ON CONFLICT DO NOTHING""")
#
#
# event.listen(
#     User.__table__, 'after_create',
#     create_admin()
# )
