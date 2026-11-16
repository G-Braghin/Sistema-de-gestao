from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import PositiveInt

from src.api.dependencies.autenticacao import UsuarioLogado
from src.api.dependencies.services import VendaServiceDep
from src.api.schemas.venda import (
    VendaItem,
    VendaLista,
    VendaResponse,
    VendaResumoFiltro,
)
from src.models import Venda

router = APIRouter(prefix='/vendas', tags=['vendas'])


@router.post(
    '/{id_cliente}/vender', response_model=VendaResponse, status_code=HTTPStatus.CREATED
)
def realizar_venda(
    usuario_logado: UsuarioLogado,
    id_cliente: PositiveInt,
    itens: list[VendaItem],
    service: VendaServiceDep,
) -> Venda:
    try:
        itens_dict = [item.model_dump() for item in itens]
        venda = service.realizar_venda(usuario_logado, id_cliente, itens_dict)

        return venda
    except ValueError as erro:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_CONTENT, detail=str(erro)
        ) from erro
    except LookupError as erro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=str(erro)
        ) from erro


@router.post(
    '/{id_venda}/cancelar', response_model=VendaResponse, status_code=HTTPStatus.CREATED
)
def cancelar_venda(
    usuario_logado: UsuarioLogado, id_venda: PositiveInt, service: VendaServiceDep
) -> Venda:
    try:
        venda = service.cancelar_venda(usuario_logado, id_venda)

        return venda
    except LookupError as erro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=str(erro)
        ) from erro
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro


@router.get('/listar', response_model=VendaLista)
def listar_resumo(
    usuario_logado: UsuarioLogado,
    filtros: Annotated[VendaResumoFiltro, Query()],
    service: VendaServiceDep,
):
    try:
        vendas = service.listar_resumo(
            usuario_logado,
            filtros.status_venda,
            filtros.filtro_data,
            filtros.inicio_filtro,
            filtros.final_filtro,
        )

        return {'vendas': vendas}
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro


@router.get('/{id_venda}/listar-detalhe', response_model=VendaResponse)
def listar_detalhe(
    usuario_logado: UsuarioLogado, id_venda: PositiveInt, service: VendaServiceDep
) -> Venda:
    try:
        venda = service.listar_venda_itens(usuario_logado, id_venda)

        return venda
    except LookupError as erro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=str(erro)
        ) from erro
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro
