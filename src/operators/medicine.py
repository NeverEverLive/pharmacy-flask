import logging
from typing import List
import uuid

from src.schemas.medicine import MedicineSchema, MedicinesSchema
from src.schemas.response import ResponseSchema
from src.schemas.medicine_substance import MedicineSubstanceSchema
from src.models.medicine import Medicine
from src.models.substance import Substance
from src.models.base_model import get_session
from src.models.logger import Logger
from src.operators.medicient_substance import create_medicine_substance, delete_relation, get_relation_by_medicine_id


def create_medicine(medicine: MedicineSchema) -> ResponseSchema:
    medicine_state = Medicine().fill(**medicine.dict())

    with get_session() as session:
        session.add(medicine_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "medicine",
            "action": "delete",
            "object_info": MedicineSchema.from_orm(medicine_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=MedicineSchema.from_orm(medicine_state),
            message="Medicine created successfuly",
            success=True
        )


def get_all_medicines() -> ResponseSchema:
    with get_session() as session:
        medicine_state = session.query(Medicine).order_by(Medicine.created_on.desc()).all()

        data = MedicinesSchema.from_orm(medicine_state).dict(by_alias=True)["data"]

        return ResponseSchema(
            data=data,
            success=True
        )


def get_medicine(id: str) -> ResponseSchema:
    with get_session() as session:
        medicine_state = session.query(Medicine).filter_by(id=id).first()

        if not medicine_state:
            return ResponseSchema(
                success=False,
                message="Same medicine doesn't exist"
            )

        return ResponseSchema(
            data=MedicineSchema.from_orm(medicine_state),
            success=True
        )


def update_medicine(medicine: Medicine, substances: List[Substance]) -> ResponseSchema:
    with get_session() as session:
        medicine_state = session.query(Medicine).filter_by(id=medicine.id).first()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "medicine",
            "action": "update",
            "object_info": MedicineSchema.from_orm(medicine_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        medicine_state.name = medicine.name
        medicine_state.description = medicine.description

        substances_relation_cross = []
        relations = get_relation_by_medicine_id(medicine.id).data
        for substance in substances:
            for relation in relations:
                if substance.id == relation["substance_id"]:
                    substances_relation_cross.append(substance.id)

        for relation in relations:
            if relation["substance_id"] not in substances_relation_cross:
                delete_relation(relation["id"])
        
        for substance in substances:
            if substance.id not in substances_relation_cross:
                create_medicine_substance(
                    MedicineSubstanceSchema(
                        substance_id=substance.id,
                        medicine_id=medicine.id
                    )
                )
        
        session.commit()

        return ResponseSchema(
            data=MedicineSchema.from_orm(medicine_state),
            message="Medicine updated",
            success=True
        )


def delete_medicine(id: str) -> ResponseSchema:
    with get_session() as session:
        medicine_state = session.query(Medicine).filter_by(id=id).first()

        if not medicine_state:
            return ResponseSchema(
                success=False,
                message="Same medicine doesn't exist"
            )

        relations = get_relation_by_medicine_id(medicine_state.id).data
        for relation in relations:
            logging.warning(relation)
            logger_data = {
                "id": uuid.uuid4(),
                "table": "medicine_substance",
                "action": "insert",
                "object_info": MedicineSubstanceSchema.parse_obj(relation).dict()
            }
            logger_state = Logger().fill(**logger_data)
            session.add(logger_state)
            session.commit()

        session.delete(medicine_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "medicine",
            "action": "insert",
            "object_info": MedicineSchema.from_orm(medicine_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=MedicineSchema.from_orm(medicine_state),
            message="Medicine deleted",
            success=True
        )
