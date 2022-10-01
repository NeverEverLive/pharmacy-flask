import datetime
import uuid

from sqlalchemy import Column, PrimaryKeyConstraint, func
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime, Date, Integer
from sqlalchemy.dialects.postgresql import UUID

from src.models.base_model import BaseModel


class Check(BaseModel):
    __tablename__ = 'check'

    id = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4())
    date = Column(Date, default=func.current_date())
    total_price = Column(Integer, nullable=False, default=0)
    created_on = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=datetime.datetime.now)

    order = relationship("Order", back_populates="check")

    __table_args__ = (
        PrimaryKeyConstraint(id),
    )
