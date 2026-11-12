from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from src.api.dependencies.autenticacao import UsuarioLogado
from src.api.dependencies.services import ClienteServiceDep
from src.api.schemas.cliente import (
    ClienteAtualizar,
    ClienteBuscarCpf,
    ClienteCadastro,
    ClienteDetalhes,
    ClienteListar,
    FiltroClienteListar,
)
from src.api.schemas.common import AtualizarStatus, Mensagem
from src.models import Cliente

router = APIRouter(prefix='/clientes', tags=['clientes'])


@router.post(
    '/cadastro', response_model=ClienteDetalhes, status_code=HTTPStatus.CREATED
)
def cadastrar_cliente(
    usuario_logado: UsuarioLogado, dados: ClienteCadastro, service: ClienteServiceDep
) -> Cliente:
    try:
        cliente = service.cadastrar_cliente(
            dados.nome, dados.cpf, dados.telefone, dados.endereco
        )
        return cliente
    except ValueError as erro:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=str(erro)
        ) from erro


@router.post('/buscar', response_model=ClienteDetalhes)
def buscar_info_cliente_por_cpf(
    usuario_logado: UsuarioLogado,
    cpf_cliente: ClienteBuscarCpf,
    service: ClienteServiceDep,
) -> Cliente:
    try:
        cliente = service.buscar_cliente_cpf(cpf_cliente.cpf)
        return cliente
    except ValueError as erro:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=str(erro)
        ) from erro
    except LookupError as erro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=str(erro)
        ) from erro


@router.patch('/{id_cliente}/atualizar-info', response_model=ClienteDetalhes)
def atualizar_cliente(
    usuario_logado: UsuarioLogado,
    id_cliente: int,
    dados: ClienteAtualizar,
    service: ClienteServiceDep,
) -> Cliente:
    try:
        cliente = service.atualizar(
            id_cliente,
            nome=dados.nome,
            endereco=dados.endereco,
            telefone=dados.telefone,
        )
        return cliente
    except ValueError as erro:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=str(erro)
        ) from erro
    except LookupError as erro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=str(erro)
        ) from erro


@router.patch('/{id_cliente}/status', response_model=Mensagem)
def mudar_status_cliente(
    usuario_logado: UsuarioLogado,
    id_cliente: int,
    status: AtualizarStatus,
    service: ClienteServiceDep,
) -> dict[str, str]:
    try:
        cliente = service.atualizar_status(usuario_logado, id_cliente, status.ativo)
        status = 'ativado' if cliente.ativo else 'desativado'

        return {'mensagem': f'Cliente {cliente.nome} {status} com sucesso.'}
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


@router.get('/listar', response_model=ClienteListar)
def listar_clientes(
    usuario_logado: UsuarioLogado,
    filtro: Annotated[FiltroClienteListar, Query()],
    service: ClienteServiceDep,
) -> dict[str, list[Cliente]]:
    try:
        clientes = service.listar(usuario_logado, filtro.ativo)

        return {'clientes': clientes}
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro
