import jwt
from os.path import join
from os import environ
from datetime import datetime, timedelta
from dotenv import load_dotenv
from uuid import UUID


load_dotenv(join('./.env'))
SECRET_KEY = str(environ.get("SECRET_KEY"))


def encode_jwt_token(user_id: UUID) -> str:
    """
    Генерирует JWT токен

    Входящие параметры:
    :params user_id: uuid пользователя

    Исходящие параметры:
    JWT токен
    """
    
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.now(),
            'sub': str(user_id)
        }
        
        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        return e


def decode_jwt_token(token: str) -> str:
    """
    Декодирует JWT токен
    
    Входные параметры:
    :params token: токен

    Исходящие параметры:
    uuid пользователя
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        if datetime.now() > datetime.fromtimestamp(payload['exp']):
            raise jwt.ExpiredSignatureError()

        return payload['sub']
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError('Signature expired. Please log in again.')
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError('Invalid token. Please log in again.')
