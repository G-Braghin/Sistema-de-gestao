from typing import Annotated

from fastapi import Depends

from src.api.dependencies.database import SessionDep
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.produto_repository import ProdutoRepository
from src.repositories.usuario_repository import UsuarioRepository


def get_usuario_repository(session: SessionDep) -> UsuarioRepository:
    return UsuarioRepository(session)


UsuarioRepositoryDep = Annotated[UsuarioRepository, Depends(get_usuario_repository)]


def get_cliente_repository(session: SessionDep) -> ClienteRepository:
    return ClienteRepository(session)


ClienteRepositoryDep = Annotated[ClienteRepository, Depends(get_cliente_repository)]


def get_produto_repository(session: SessionDep) -> ProdutoRepository:
    return ProdutoRepository(session)


ProdutoRepositoryDep = Annotated[ProdutoRepository, Depends(get_produto_repository)]
