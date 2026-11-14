from typing import Annotated

from fastapi import Depends

from src.api.dependencies.repositories import (
    ClienteRepositoryDep,
    MovimentacaoRepositoryDep,
    ProdutoRepositoryDep,
    UsuarioRepositoryDep,
)
from src.services.autenticacao_service import AutenticacaoService
from src.services.cliente_service import ClienteService
from src.services.estoque_service import EstoqueService
from src.services.produto_service import ProdutoService
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


def get_cliente_service(repository: ClienteRepositoryDep):
    return ClienteService(repository)


ClienteServiceDep = Annotated[ClienteService, Depends(get_cliente_service)]


def get_produto_service(repository: ProdutoRepositoryDep):
    return ProdutoService(repository)


ProdutoServiceDep = Annotated[ProdutoService, Depends(get_produto_service)]


def get_estoque_service(
    mov_repository: MovimentacaoRepositoryDep, prod_repository: ProdutoRepositoryDep
):
    return EstoqueService(prod_repository, mov_repository)


EstoqueServiceDep = Annotated[EstoqueService, Depends(get_estoque_service)]
