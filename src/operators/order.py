import uuid

from src.schemas.order import OrderSchema, OrdersSchema
from src.schemas.response import ResponseSchema
from src.models.order import Order
from src.models.base_model import get_session
from src.models.logger import Logger


def create_order(order: OrderSchema) -> ResponseSchema:
    order_state = Order().fill(**order.dict())

    with get_session() as session:
        session.add(order_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "order",
            "action": "delete",
            "object_info": OrderSchema.from_orm(order_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=OrderSchema.from_orm(order_state),
            message="Order created successfuly",
            success=True
        )


def get_orders_by_user_id(id: str) -> ResponseSchema:
    with get_session() as session:
        order_state = session.query(Order).filter_by(user_id=id).all()

        if not order_state:
            return ResponseSchema(
                data=[],
                success=False,
                message="Same order doesn't exist"
            )

        return ResponseSchema(
            data=OrdersSchema.from_orm(order_state).dict(by_alias=True)["data"],
            success=True
        )
