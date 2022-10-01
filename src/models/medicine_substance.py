
import datetime
import uuid

from sqlalchemy import Column, func, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from src.models.base_model import BaseModel


class MedicineSubstance(BaseModel):
    __tablename__ = 'medicine_substance'

    id = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4())
    medicine_id = Column(UUID(as_uuid=True), nullable=False)
    substance_id = Column(UUID(as_uuid=True), nullable=False)
    created_on = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=datetime.datetime.now)
    
    substance = relationship("Substance", back_populates="substance_relation", uselist=True)
    medicine = relationship("Medicine", back_populates="medicine_relation", uselist=True)

    __table_args__ = (
        PrimaryKeyConstraint(id),
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
                substance_id,
            ),
            (
                "substance.id",
            )
        ),
    )