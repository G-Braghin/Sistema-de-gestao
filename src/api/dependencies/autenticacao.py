from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError, decode

from src.api.dependencies.repositories import UsuarioRepositoryDep
from src.settings import Settings

oauth2_schema = OAuth2PasswordBearer(tokenUrl='autenticacao/login')
settings = Settings()


def get_current_user(
    repository: UsuarioRepositoryDep, token: str = Depends(oauth2_schema)
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Nao foi possivel validar as credenciais',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        id_usuario = payload.get('sub')

        if not isinstance(id_usuario, str) or not id_usuario.isdigit():
            raise credentials_exception

    except InvalidTokenError as err:
        raise credentials_exception from err

    usuario = repository.buscar_por_id(int(id_usuario))

    if not usuario or not usuario.ativo:
        raise credentials_exception

    return usuario
