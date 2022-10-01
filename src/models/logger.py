import datetime
import uuid

from sqlalchemy import Column, func, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.types import String, DateTime, Boolean

from src.models.base_model import BaseModel


class Logger(BaseModel):
    __tablename__ = 'logger'

    id = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4())
    table = Column(String, nullable=False)
    action = Column(String, nullable=False)
    object_info = Column(JSONB, nullable=False)
    executed = Column(Boolean, default=False)
    inserted_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=datetime.datetime.now())
    
    __table_args__ = (
        PrimaryKeyConstraint(id),
    )
