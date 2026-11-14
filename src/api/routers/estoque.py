from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from pydantic import PositiveInt

from src.api.dependencies.autenticacao import UsuarioLogado
from src.api.dependencies.services import EstoqueServiceDep
from src.api.schemas.estoque import (
    ListarMovimentacao,
    ModificarEstoqueEntrada,
    ModificarEstoqueSaida,
    MovimentacaoEstoque,
)
from src.models import Movimentacao

router = APIRouter(prefix='/estoque', tags=['estoque'])


@router.post(
    '/{id_produto}/entrada',
    response_model=MovimentacaoEstoque,
    status_code=HTTPStatus.CREATED,
)
def entrada_estoque(
    usuario_logado: UsuarioLogado,
    id_produto: PositiveInt,
    dados: ModificarEstoqueEntrada,
    service: EstoqueServiceDep,
) -> Movimentacao:
    try:
        movimentacao = service.dar_entrada(
            usuario_logado, id_produto, dados.quantidade, dados.motivo
        )

        return movimentacao
    except LookupError as erro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=str(erro)
        ) from erro
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro


@router.post(
    '/{id_produto}/saida',
    response_model=MovimentacaoEstoque,
    status_code=HTTPStatus.CREATED,
)
def saida_estoque(
    usuario_logado: UsuarioLogado,
    id_produto: PositiveInt,
    dados: ModificarEstoqueSaida,
    service: EstoqueServiceDep,
) -> Movimentacao:
    try:
        movimentacao = service.dar_saida(
            usuario_logado, id_produto, dados.quantidade, dados.motivo
        )

        return movimentacao
    except ValueError as erro:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=str(erro)
        ) from erro
    except LookupError as erro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=str(erro)
        ) from erro
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro


@router.get('/listar', response_model=ListarMovimentacao)
def listar_movimentacao(usuario_logado: UsuarioLogado, service: EstoqueServiceDep):
    try:
        movimentacoes = service.listar_movimentacoes(usuario_logado)

        return {'movimentacoes': movimentacoes}
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro
