import uuid

from src.schemas.doctor import DoctorSchema, DoctorsSchema
from src.schemas.response import ResponseSchema
from src.models.doctor import Doctor
from src.models.base_model import get_session
from src.models.logger import Logger


def create_doctor(doctor: DoctorSchema) -> ResponseSchema:
    doctor_state = Doctor().fill(**doctor.dict())

    with get_session() as session:
        session.add(doctor_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "doctor",
            "action": "delete",
            "object_info": DoctorSchema.from_orm(doctor_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=DoctorSchema.from_orm(doctor_state),
            message="Doctor created successfuly",
            success=True
        )


def get_all_doctors() -> ResponseSchema:
    with get_session() as session:
        doctors_state = session.query(Doctor).order_by(Doctor.created_on.desc()).all()

        data = DoctorsSchema.from_orm(doctors_state).dict(by_alias=True)["data"]

        return ResponseSchema(
            data=data,
            success=True
        )


def get_doctor(id: str) -> ResponseSchema:
    with get_session() as session:
        doctor_state = session.query(Doctor).filter_by(id=id).first()

        if not doctor_state:
            return ResponseSchema(
                success=False,
                message="Same doctor doesn't exist"
            )

        return ResponseSchema(
            data=DoctorSchema.from_orm(doctor_state),
            success=True
        )


def update_doctor(doctor: DoctorSchema) -> ResponseSchema:
    with get_session() as session:
        doctor_state = session.query(Doctor).filter_by(id=doctor.id).first()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "doctor",
            "action": "update",
            "object_info": DoctorSchema.from_orm(doctor_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        doctor_state.first_name = doctor.first_name
        doctor_state.last_name = doctor.last_name
        doctor_state.hospital = doctor.hospital

        session.commit()

        return ResponseSchema(
            data=DoctorSchema.from_orm(doctor_state),
            message="Doctor updated",
            success=True
        )


def delete_doctor(id: int) -> ResponseSchema:
    with get_session() as session:
        doctor_state = session.query(Doctor).filter_by(id=id).first()

        if not doctor_state:
            return ResponseSchema(
                success=False,
                message="Same doctor doesn't exist"
            )

        session.delete(doctor_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "doctor",
            "action": "insert",
            "object_info": DoctorSchema.from_orm(doctor_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=DoctorSchema.from_orm(doctor_state),
            message="Doctor deleted",
            success=True
        )
