import datetime
import uuid

from sqlalchemy import Column, PrimaryKeyConstraint, func, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from src.models.base_model import BaseModel


class Recipe(BaseModel):
    __tablename__ = 'recipe'

    id = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4())
    doctor_id = Column(UUID(as_uuid=True), nullable=False)
    medicine_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    electronic_signature = Column(String, unique=False, nullable=False)
    created_on = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=datetime.datetime.now)
    
    doctor = relationship("Doctor", back_populates="recipe")
    medicine = relationship("Medicine", back_populates="recipe")
    order = relationship("Order", back_populates="recipe", uselist=False)

    __table_args__ = (
        PrimaryKeyConstraint(id),
        ForeignKeyConstraint(
            (
                doctor_id,
            ),
            (
                "doctor.id",
            )
        ),
        ForeignKeyConstraint(
            (
                medicine_id,
            ),
            (
                "medicine.id",
            )
        ),
        ForeignKeyConstraint(
            (
                user_id,
            ),
            (
                "user.id",
            )
        ),
    )
