import datetime
import uuid

from sqlalchemy import Column, PrimaryKeyConstraint, func
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from src.models.base_model import BaseModel


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