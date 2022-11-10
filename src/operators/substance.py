import logging
import uuid

from src.operators.medicient_substance import get_relation_by_substance_id
from src.schemas.supplier import SupplierSchema
from src.schemas.substance import SubstanceSchema, SubstancesSchema
from src.schemas.medicine_substance import MedicineSubstanceSchema
from src.schemas.response import ResponseSchema
from src.models.substance import Substance
from src.models.base_model import get_session
from src.models.logger import Logger


def create_substance(substance: SubstanceSchema) -> ResponseSchema:
    substance_state = Substance().fill(**substance.dict())

    with get_session() as session:
        session.add(substance_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "substance",
            "action": "delete",
            "object_info": SubstanceSchema.from_orm(substance_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=SubstanceSchema.from_orm(substance_state),
            message="Substance created successfuly",
            success=True
        )


def get_all_substances() -> ResponseSchema:
    with get_session() as session:
        substance_state = session.query(Substance).order_by(Substance.created_on.desc()).all()

        data = SubstancesSchema.from_orm(substance_state).dict(by_alias=True)["data"]

        return ResponseSchema(
            data=data,
            success=True
        )


def get_substance(id: str) -> ResponseSchema:
    with get_session() as session:
        substance_state = session.query(Substance).filter_by(id=id).first()

        if not substance_state:
            return ResponseSchema(
                success=False,
                message="Same substance doesn't exist"
            )

        return ResponseSchema(
            data=SubstanceSchema.from_orm(substance_state),
            success=True
        )


def update_substance(substance: SubstanceSchema) -> ResponseSchema:
    with get_session() as session:
        substance_state = session.query(Substance).filter_by(id=substance.id).first()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "substance",
            "action": "update",
            "object_info": SubstanceSchema.from_orm(substance_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        substance_state.name = substance.name

        session.commit()

        return ResponseSchema(
            data=SubstanceSchema.from_orm(substance_state),
            message="Substance updated",
            success=True
        )


def delete_substance(id: str) -> ResponseSchema:
    with get_session() as session:
        substance_state = session.query(Substance).filter_by(id=id).first()

        if not substance_state:
            return ResponseSchema(
                success=False,
                message="Same substance doesn't exist"
            )

        try:
            relations = get_relation_by_substance_id(substance_state.id).data
        except:
            relations = []
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

        session.delete(substance_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "substance",
            "action": "insert",
            "object_info": SubstanceSchema.from_orm(substance_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=SubstanceSchema.from_orm(substance_state),
            message="Substance deleted",
            success=True
        )
