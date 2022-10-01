from uuid import UUID, uuid4
import logging
from typing import Dict, Union

import bcrypt
from sqlalchemy import inspect

from src.models.user import User, CreateUpdateUserSchema
from src.operators.jwt_token import decode_jwt_token, encode_jwt_token


def create_user(data: Dict[str, str]) -> Dict[str, str]:
    """Создать пользователя
        Входные параметры:
        :params data: Данные пользователя

        Исходящие данные:
        :params output_data: Словарь с результатами
    """
    data['id'] = uuid4()
    data['hash_password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    serializer = CreateUpdateUserSchema()
    data = serializer.dump(data)

    logging.warning(data)

    new_user = User().fill(**data)
    new_user.save()

    output_data = {
        'success': True,
        'message': 'User created',
        "user": {
            "id": data["id"],
            "username": data["username"]
        }
    }

    return output_data


def update_user(data: Dict[str, str], token: str) -> Dict[str, Union[str, bool]]:
    """Изменить пользователя
        Входные параметры:
        :params data: Данные пользователя
        :params token: JWT токен

        Исходящие данные:
        :params output_data: Словарь с результатами
    """

    if data.get('password'):
        data['hash_password'] = bcrypt.hashpw(data.get('password').encode('utf-8'), bcrypt.gensalt())

    serializer = CreateUpdateUserSchema()
    data = serializer.dump(data)


    id = decode_jwt_token(token)
    if id is None:
        raise KeyError("'id' is required argument to update")

    user_to_update = User.get_by_id(id)

    mapper = inspect(User)
    attrs = [column.key for column in mapper.attrs]


    for attr, value in data.items():
        if attr in attrs:
            setattr(user_to_update, attr, value)
    
    user_to_update.save()

    output_data = {
        'success': True,
        'message': 'User updated'
    }

    logging.debug(f"out {output_data}")

    return output_data


def delete_user(token: str) -> Dict[str, Union[str, bool]]:
    """Удалить пользователя
        Входные параметры:
        :params token: JWT токен

        Исходящие данные:
        :params output_data: Словарь с результатами
    """
    id = decode_jwt_token(token)
    if id is None:
        raise KeyError("'id' is required argument to update")

    user_to_delete = User.get_by_id(id)
    user_to_delete.delete()

    output_data = {
        'success': True,
        'message': 'User deleted'
    }

    return output_data 


def get_user(id: UUID) -> Dict[str, Union[str, bool, Dict[str, str]]]:
    """Вернуть пользователя
        
        Входные параметры:
        :params data: Данные пользователя

        Исходящие параметры:
        :params data: Словарь с результатами
    """
    user = User.get_by_id(id)
    data = {
        'success': True,
        'user': {
            "id": user.id,
            "username": user.username,
            "created_on": user.created_on
        }
    }
    return data


def login_user(data: Dict[str, str]) -> Dict[str, Union[str, bool, Dict[str, str]]]:
    """Авторизировать пользователя
    
        Входные параметры:
        :params data: Данные пользователя

        Исходящие параметры:
        :params output_data: Словарь с результатами
    """
    user = User.get_by_username(data['username'])
    if user is None:
        raise ValueError('Incorrect username')

    if not bcrypt.checkpw(data['password'].encode('utf-8'), user.hash_password.encode('utf-8')):
        raise ValueError('Incorrect password')

    token = encode_jwt_token(user.id)
    output_data = {
        'success': True,
        'message': "You're logged in successfuly",
        'user': {
            "id": user.id,
            "username": user.username,
            "created_on": user.created_on,
            "token": token
        }
    }
    print(output_data)
    return output_data
