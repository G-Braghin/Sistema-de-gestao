from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response

from src.api.dependencies.autenticacao import UsuarioLogado
from src.api.dependencies.services import EstoqueServiceDep, VendaServiceDep
from src.api.schemas.produto import ListarProdutos
from src.api.schemas.relatorio import (
    EstoqueFiltro,
    ListaProdutosVendidos,
    RelatorioData,
    RelatorioEstoqueRes,
    RelatorioVendaRes,
)
from src.dtos.produtos_vendidos_resumo import ProdutosVendidosResumo
from src.dtos.relatorio_venda_resumo import RelatorioVendaResumo
from src.models import Produto
from src.utils.exportacao_csv import (
    exportar_estoque_csv,
    exportar_produtos_vendidos_csv,
    exportar_resumo_vendas_csv,
)

router = APIRouter(prefix='/relatorios', tags=['relatorios'])


@router.get('/venda-resumo', response_model=RelatorioVendaRes)
def relatorio_resumo_venda(
    usuario_logado: UsuarioLogado,
    data: Annotated[RelatorioData, Query()],
    service: VendaServiceDep,
) -> RelatorioVendaResumo:
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
) -> dict[str, list[Produto]]:
    try:
        relatorio = service.relatorio_estoque_baixo(usuario_logado, filtro.limite)

        return {'produtos': relatorio}
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro


@router.get('/venda-resumo/exportar')
def exportar_venda_resumo(
    usuario_logado: UsuarioLogado,
    data: Annotated[RelatorioData, Query()],
    service: VendaServiceDep,
) -> Response:
    try:
        relatorio = service.criar_resumo_relatorio(
            usuario_logado, data.inicio, data.fim
        )

        conteudo = exportar_resumo_vendas_csv(relatorio)

        return Response(
            content='\ufeff' + conteudo,
            media_type='text/csv',
            headers={
                'Content-Disposition': ('attachment; filename="resumo_vendas.csv"')
            },
        )

    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=str(erro),
        ) from erro


@router.get('/produtos-vendidos/exportar')
def exportar_produtos_vendidos(
    usuario_logado: UsuarioLogado,
    data: Annotated[RelatorioData, Query()],
    service: VendaServiceDep,
) -> Response:
    try:
        relatorios = service.relatorio_produtos(usuario_logado, data.inicio, data.fim)

        conteudo = exportar_produtos_vendidos_csv(relatorios)

        return Response(
            content='\ufeff' + conteudo,
            media_type='text/csv',
            headers={
                'Content-Disposition': ('attachment; filename="produtos_vendidos.csv"')
            },
        )

    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=str(erro),
        ) from erro


@router.get('/estoque/exportar')
def exportar_relatorio_estoque(
    usuario_logado: UsuarioLogado,
    service: EstoqueServiceDep,
) -> Response:
    try:
        relatorios = service.relatorio_estoque(usuario_logado)

        conteudo = exportar_estoque_csv(relatorios)

        return Response(
            content='\ufeff' + conteudo,
            media_type='text/csv',
            headers={
                'Content-Disposition': ('attachment; filename="relatorio_estoque.csv"')
            },
        )

    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=str(erro),
        ) from erro
