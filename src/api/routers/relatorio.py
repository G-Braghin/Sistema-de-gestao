from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from src.api.dependencies.services import EstoqueServiceDep, VendaServiceDep
from src.api.routers.cliente import UsuarioLogado
from src.api.schemas.produto import ListarProdutos
from src.api.schemas.relatorio import (
    EstoqueFiltro,
    ListaProdutosVendidos,
    RelatorioData,
    RelatorioEstoqueRes,
    RelatorioVendaRes,
)
from src.entities.dtos.produtos_vendidos_resumo import ProdutosVendidosResumo
from src.entities.dtos.relatorio_venda_resumo import RelatorioVendaResumo

router = APIRouter(prefix='/relatorios', tags=['relatorios'])


@router.get('/venda-resumo', response_model=RelatorioVendaRes)
def relatorio_resumo_venda(
    usuario_logado: UsuarioLogado,
    data: Annotated[RelatorioData, Query()],
    service: VendaServiceDep,
) -> None | RelatorioVendaResumo:
    try:
        relatorio = service.criar_resumo_relatorio(
            usuario_logado, data.inicio, data.fim
        )

        return relatorio
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro


@router.get('/produtos-vendidos', response_model=ListaProdutosVendidos)
def relatorio_produtos_mais_vendidos(
    usuario_logado: UsuarioLogado,
    data: Annotated[RelatorioData, Query()],
    service: VendaServiceDep,
) -> dict[str, list[ProdutosVendidosResumo]]:
    try:
        relatorios = service.relatorio_produtos(usuario_logado, data.inicio, data.fim)

        return {'produtos': relatorios}
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro


@router.get('/estoque', response_model=RelatorioEstoqueRes)
def relatorio_estoque(usuario_logado: UsuarioLogado, service: EstoqueServiceDep):
    try:
        relatorio = service.relatorio_estoque(usuario_logado)

        return relatorio
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro


@router.get('/estoque-limite', response_model=ListarProdutos)
def relatorio_estoque_baixo(
    usuario_logado: UsuarioLogado,
    filtro: Annotated[EstoqueFiltro, Query()],
    service: EstoqueServiceDep,
):
    try:
        relatorio = service.relatorio_estoque_baixo(usuario_logado, filtro.limite)

        return {'produtos': relatorio}
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro
