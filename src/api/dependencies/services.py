from typing import Annotated

from fastapi import Depends

from src.api.dependencies.repositories import UsuarioRepositoryDep
from src.services.autenticacao_service import AutenticacaoService
from src.services.usuario_service import UsuarioService


def get_autenticacao_service(
    repository: UsuarioRepositoryDep,
) -> AutenticacaoService:
    return AutenticacaoService(repository)


AutenticacaoServiceDep = Annotated[
    AutenticacaoService,
    Depends(get_autenticacao_service),
]


def get_usuario_service(
    repository: UsuarioRepositoryDep,
    auth: AutenticacaoServiceDep,
) -> UsuarioService:
    return UsuarioService(repository, auth)


UsuarioServiceDep = Annotated[
    UsuarioService,
    Depends(get_usuario_service),
]
