import logging

from src.models.base_model import get_session, set_session, Base

from src.models.check import Check
from src.models.doctor import Doctor
from src.models.medicine_substance import MedicineSubstance
from src.models.medicine import Medicine
from src.models.substance import Substance
from src.models.order import Order
from src.models.recipe import Recipe
from src.models.supplier import Supplier
from src.models.role import Role
from src.models.user import User
from src.models.logger import Logger

set_session()


from src.schemas.user import UserSchema
from sqlalchemy import select

with get_session() as session:
    admin_user = {
        # "id": uuid.uuid4(),
        "username": "admin",
        "password": "123",
        "role_id": session.execute(select(Role.id).where(Role.name == "admin")).scalar()
    }
    serializing_data = UserSchema.parse_obj(admin_user)
    session.execute(f"""INSERT INTO "user"(id, username, hash_password, role_id)
                VALUES
                ('{serializing_data.id}', '{serializing_data.username}', '{serializing_data.hash_password}', '{serializing_data.role_id}')
                ON CONFLICT DO NOTHING""")
    session.commit()
