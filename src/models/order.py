import datetime
import uuid

from sqlalchemy import Column, PrimaryKeyConstraint, func, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from src.models.base_model import BaseModel


class Order(BaseModel):
    __tablename__ = 'order'

    id = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4())
    recipe_id = Column(UUID(as_uuid=True), nullable=False)
    supplier_id = Column(UUID(as_uuid=True), nullable=False)
    check_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, unique=True, nullable=False)
    created_on = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=datetime.datetime.now)
    
    recipe = relationship("Recipe", back_populates="order", uselist=True)
    check = relationship("Check", back_populates="order", uselist=False)
    supplier = relationship("Supplier", back_populates="order", uselist=False)
    user = relationship("User", back_populates="order", uselist=False)

    __table_args__ = (
        PrimaryKeyConstraint(id),
        ForeignKeyConstraint(
            (
                recipe_id,
            ),
            (
                "recipe.id",
            )
        ),
        ForeignKeyConstraint(
            (
                supplier_id,
            ),
            (
                "supplier.id",
            )
        ),
        ForeignKeyConstraint(
            (
                check_id,
            ),
            (
                "check.id",
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