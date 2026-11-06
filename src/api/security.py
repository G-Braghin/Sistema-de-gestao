from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from jwt import encode

from src.settings import Settings

settings = Settings()


def criar_token(id_usuario: int):
    expire = datetime.now(ZoneInfo('UTC')) + timedelta(minutes=120)
    to_encode = {'sub': str(id_usuario), 'exp': expire}

    encoded_jwt = encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt
