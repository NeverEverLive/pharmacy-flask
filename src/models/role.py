import datetime
import uuid
import logging

from sqlalchemy import Column, PrimaryKeyConstraint, func, event, DDL
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from src.models.base_model import BaseModel
from src.schemas.role import RoleSchema


class Role(BaseModel):
    __tablename__ = 'role'

    id = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4())
    name = Column(String, unique=True, nullable=False)
    created_on = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=datetime.datetime.now)
    
    user = relationship("User", back_populates="role", uselist=True)

    __table_args__ = (
        PrimaryKeyConstraint(id),
    )

#
# def create_admin_role():
#     """DDL при создании таблицы добавляет роль admin"""
#     admin_user = {
#         "name": "admin_role",
#     }
#
#     serializing_data = RoleSchema.parse_obj(admin_user)
#     return DDL(f"""INSERT INTO "role"(id, name)
#                 VALUES
#                 ('{serializing_data.id}', '{serializing_data.name}')
#                 ON CONFLICT DO NOTHING""")
#
#
# event.listen(
#     Role.__table__, 'after_create',
#     create_admin_role()
# )