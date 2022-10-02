import logging
import uuid

from src.schemas.medicine_substance import MedicineSubstanceSchema, RelationsSchema
from src.schemas.response import ResponseSchema
from src.models.medicine_substance import MedicineSubstance
from src.models.base_model import get_session
from src.models.logger import Logger


def create_medicine_substance(medicine_substance: MedicineSubstanceSchema) -> ResponseSchema:
    medicine_substance_state = MedicineSubstance().fill(**medicine_substance.dict())

    with get_session() as session:
        session.add(medicine_substance_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "medicine_substance",
            "action": "delete",
            "object_info": MedicineSubstanceSchema.from_orm(medicine_substance_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=MedicineSubstanceSchema.from_orm(medicine_substance_state),
            message="MedicineSubstance created successfuly",
            success=True
        )


def get_relation_by_medicine_id(id: str) -> ResponseSchema:
    with get_session() as session:
        relation_state = session.query(MedicineSubstance).filter_by(medicine_id=id).all()

        if not relation_state:
            return ResponseSchema(
                data=[],
                success=False,
                message="Same medicine doesn't exist"
            )

        return ResponseSchema(
            data=RelationsSchema.from_orm(relation_state).dict(by_alias=True)["data"],
            success=True
        )


def get_relation_by_substance_id(id: str) -> ResponseSchema:
    with get_session() as session:
        relation_state = session.query(MedicineSubstance).filter_by(substance_id=id).all()

        if not relation_state:
            return ResponseSchema(
                data=[],
                success=False,
                message="Same medicine doesn't exist"
            )

        return ResponseSchema(
            data=RelationsSchema.from_orm(relation_state).dict(by_alias=True)["data"],
            success=True
        )


def delete_relation(id: str) -> ResponseSchema:
    with get_session() as session:
        relation_state = session.query(MedicineSubstance).filter_by(id=id).first()

        if not relation_state:
            return ResponseSchema(
                success=False,
                message="Same relation doesn't exist"
            )

        session.delete(relation_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "relation",
            "action": "insert",
            "object_info": MedicineSubstanceSchema.from_orm(relation_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=MedicineSubstanceSchema.from_orm(relation_state),
            message="Relation deleted",
            success=True
        )

