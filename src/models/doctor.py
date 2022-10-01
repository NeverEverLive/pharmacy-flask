
import datetime
import uuid

from sqlalchemy import Column, PrimaryKeyConstraint, func
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from src.models.base_model import BaseModel


class Doctor(BaseModel):
    __tablename__ = 'doctor'

    id = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4())
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hospital = Column(String, nullable=True)
    created_on = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=datetime.datetime.now)
    
    recipe = relationship("Recipe", back_populates="doctor", uselist=True)

    __table_args__ = (
        PrimaryKeyConstraint(id),
    )
