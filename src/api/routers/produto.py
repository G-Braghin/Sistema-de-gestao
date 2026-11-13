from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from pydantic import PositiveInt

from src.api.dependencies.autenticacao import UsuarioLogado
from src.api.dependencies.services import ProdutoServiceDep
from src.api.schemas.produto import (
    ListarProdutos,
    ProdutoAtualizar,
    ProdutoCadastro,
    ProdutoInfo,
)
from src.models import Produto

router = APIRouter(prefix='/produtos', tags=['produtos'])


@router.post('/cadastro', response_model=ProdutoInfo, status_code=HTTPStatus.CREATED)
def cadastrar_produto(
    usuario_logado: UsuarioLogado, dados: ProdutoCadastro, service: ProdutoServiceDep
) -> Produto:
    produto = service.cadastrar_produto(dados.nome, dados.preco)

    return produto


@router.patch('/{id_produto}/atualizar', response_model=ProdutoInfo)
def atualizar_info(
    usuario_logado: UsuarioLogado,
    id_produto: PositiveInt,
    dados: ProdutoAtualizar,
    service: ProdutoServiceDep,
) -> Produto:
    try:
        produto = service.atualizar(id_produto, nome=dados.nome, preco=dados.preco)

        return produto
    except LookupError as erro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=str(erro)
        ) from erro


@router.get('/listar', response_model=ListarProdutos)
def listar_produto(usuario_logado: UsuarioLogado, service: ProdutoServiceDep):
    produtos = service.listar_produtos()

    return {'produtos': produtos}
