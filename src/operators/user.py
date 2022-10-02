import logging

import bcrypt

from src.models.base_model import get_session
from src.models.user import User
from src.operators.jwt_token import decode_jwt_token, encode_jwt_token
from src.schemas.response import ResponseSchema
from src.schemas.user import UserSecureSchema, UsersSecureSchema


def create_user(user) -> ResponseSchema:
    """
        Создать пользователя
        Входные параметры:
        :params user: Данные пользователя

        Исходящие данные:
        Словарь с результатами создания пользователя
    """

    user_state = User().fill(**user.dict())

    with get_session() as session:
        session.add(user_state)
        session.commit()

        return ResponseSchema(
            data=UserSecureSchema.from_orm(user),
            success=True
        )


def get_all_users() -> ResponseSchema:
    """Вернуть пользователя

        Входные параметры:
        :params data: Данные пользователя

        Исходящие параметры:
        :params data: Словарь с результатами
    """
    with get_session() as session:
        user_state = session.query(User).order_by(User.created_on.desc()).all()

        data = UsersSecureSchema.from_orm(user_state).dict(by_alias=True)["data"]

        logging.warning(data)

        return ResponseSchema(
            data=data,
            success=True
        )


def get_user(id: str) -> ResponseSchema:
    """Вернуть пользователя

        Входные параметры:
        :params data: Данные пользователя

        Исходящие параметры:
        :params data: Словарь с результатами
    """
    with get_session() as session:
        roles_state = session.query(User).filter_by(id=id).first()

        data = UserSecureSchema.from_orm(roles_state).dict()

        return ResponseSchema(
            data=data,
            success=True
        )


def update_user(user_data) -> ResponseSchema:
    """
        Изменить пользователя
        Входные параметры:
        :params user: Данные пользователя

        Исходящие данные:
        Словарь с результатами обновления пользователя
    """

    user_state = User().fill(**user_data.dict())

    with get_session() as session:
        session.merge(user_state)
        session.commit()

        return ResponseSchema(
            data=UserSecureSchema.from_orm(user_state),
            success=True
        )


def delete_user(id: str) -> ResponseSchema:
    """
        Удалить пользователя
        Входные параметры:
        :params user: Данные пользователя

        Исходящие данные:
        Словарь с результатами удаления пользователя
    """

    with get_session() as session:
        user_state = session.query(User).filter_by(id=id).first()

        if not user_state:
            ...

        session.delete(user_state)
        session.commit()

        return ResponseSchema(
            data=UserSecureSchema.from_orm(user_state),
            success=True
        )


def login(user) -> ResponseSchema:
    """
        Авторизировать пользователя

        Входные параметры:
        :params user: Данные пользователя

        Исходящие параметры:
        Словарь с результатами авторизации
    """
    user_state = User.get_by_username(user.email)
    if user_state is None:
        raise ValueError('Неверная логин')

    if not bcrypt.checkpw(user.hash_password, user_state.hash_password):
        raise ValueError('Неверный пароль')

    token = encode_jwt_token(user_state.id)

    return ResponseSchema(
        data=UserSecureSchema.from_orm(user_state),
        message="Авторизация прошла успешно",
        success=True
    )
