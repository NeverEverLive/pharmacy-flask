import logging
import uuid

from src.schemas.supplier import SupplierSchema, SuppliersSchema
from src.schemas.response import ResponseSchema
from src.models.supplier import Supplier
from src.models.base_model import get_session
from src.models.logger import Logger


def create_supplier(supplier: SupplierSchema) -> ResponseSchema:
    supplier_state = Supplier().fill(**supplier.dict())

    with get_session() as session:
        session.add(supplier_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "supplier",
            "action": "delete",
            "object_info": SupplierSchema.from_orm(supplier_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=SupplierSchema.from_orm(supplier_state),
            message="Supplier created successfuly",
            success=True
        )


def get_supplier(id: str) -> ResponseSchema:
    with get_session() as session:
        supplier_state = session.query(Supplier).filter_by(id=id).first()

        logging.warning(supplier_state)
        logging.warning(SupplierSchema.from_orm(supplier_state).dict(by_alias=True))

        if not supplier_state:
            return ResponseSchema(
                data=[],
                success=False,
                message="Same supplier doesn't exist"
            )

        return ResponseSchema(
            data=SupplierSchema.from_orm(supplier_state).dict(),
            success=True
        )


def get_all_suppliers() -> ResponseSchema:
    with get_session() as session:
        doctors_state = session.query(Supplier).order_by(Supplier.created_on.desc()).all()

        data = SuppliersSchema.from_orm(doctors_state).dict(by_alias=True)["data"]

        return ResponseSchema(
            data=data,
            success=True
        )


def update_supplier(supplier: SupplierSchema) -> ResponseSchema:
    with get_session() as session:
        supplier_state = session.query(Supplier).filter_by(id=supplier.id).first()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "supplier",
            "action": "update",
            "object_info": SupplierSchema.from_orm(supplier_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        supplier_state.name = supplier.name

        session.commit()

        return ResponseSchema(
            data=SupplierSchema.from_orm(supplier_state),
            message="Supplier updated",
            success=True
        )


def delete_supplier(id: int) -> ResponseSchema:
    with get_session() as session:
        supplier_state = session.query(Supplier).filter_by(id=id).first()

        if not supplier_state:
            return ResponseSchema(
                success=False,
                message="Same supplier doesn't exist"
            )

        session.delete(supplier_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "supplier",
            "action": "insert",
            "object_info": SupplierSchema.from_orm(supplier_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=SupplierSchema.from_orm(supplier_state),
            message="Supplier deleted",
            success=True
        )
