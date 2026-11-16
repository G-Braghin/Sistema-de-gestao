from typing import Annotated

from fastapi import Depends

from src.api.dependencies.repositories import (
    ClienteRepositoryDep,
    MovimentacaoRepositoryDep,
    ProdutoRepositoryDep,
    UsuarioRepositoryDep,
    VendaRepositoryDep,
)
from src.services.autenticacao_service import AutenticacaoService
from src.services.cliente_service import ClienteService
from src.services.estoque_service import EstoqueService
from src.services.produto_service import ProdutoService
from src.services.usuario_service import UsuarioService
from src.services.venda_service import VendaService


def get_autenticacao_service(
    repository: UsuarioRepositoryDep,
):

    return AutenticacaoService(repository)


AutenticacaoServiceDep = Annotated[
    AutenticacaoService,
    Depends(get_autenticacao_service),
]


def get_usuario_service(
    repository: UsuarioRepositoryDep,
    auth: AutenticacaoServiceDep,
):

    return UsuarioService(repository, auth)


UsuarioServiceDep = Annotated[
    UsuarioService,
    Depends(get_usuario_service),
]


def get_cliente_service(
    repository: ClienteRepositoryDep,
):

    return ClienteService(repository)


ClienteServiceDep = Annotated[ClienteService, Depends(get_cliente_service)]


def get_produto_service(
    repository: ProdutoRepositoryDep,
):

    return ProdutoService(repository)


ProdutoServiceDep = Annotated[ProdutoService, Depends(get_produto_service)]


def get_estoque_service(
    mov_repository: MovimentacaoRepositoryDep,
    prod_repository: ProdutoRepositoryDep,
):

    return EstoqueService(prod_repository, mov_repository)


EstoqueServiceDep = Annotated[EstoqueService, Depends(get_estoque_service)]


def get_venda_service(
    venda_repo: VendaRepositoryDep,
    produto_repo: ProdutoRepositoryDep,
    cliente_repo: ClienteRepositoryDep,
    estoque_serv: EstoqueServiceDep,
):

    return VendaService(venda_repo, produto_repo, cliente_repo, estoque_serv)


VendaServiceDep = Annotated[VendaService, Depends(get_venda_service)]
