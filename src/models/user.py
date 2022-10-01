import datetime
from uuid import uuid4

from sqlalchemy import Column, func, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import String, DateTime
from marshmallow import Schema, fields

from src.models.base_model import BaseModel


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
    id = fields.UUID()
    username = fields.String()
    hash_password = fields.String()
