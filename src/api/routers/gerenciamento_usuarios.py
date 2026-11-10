from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from src.api.dependencies.autenticacao import UsuarioLogado
from src.api.dependencies.services import UsuarioServiceDep
from src.api.schemas.usuario import AtualizarStatus, Mensagem, ResetarSenha

router = APIRouter(prefix='/usuarios', tags=['Gerenciamento-Usuario'])


@router.patch('/{id_usuario}/promover', response_model=Mensagem)
def promover_gerente(
    usuario_logado: UsuarioLogado, id_usuario: int, service: UsuarioServiceDep
):
    try:
        usuario = service.promover_a_gerente(usuario_logado, id_usuario)

        return {'mensagem': f'{usuario.nome} foi promovido com sucesso.'}
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


@router.patch('/{id_usuario}/atualizar-status', response_model=Mensagem)
def atualizar_status(
    usuario_logado: UsuarioLogado,
    id_usuario: int,
    dados: AtualizarStatus,
    service: UsuarioServiceDep,
):
    try:
        usuario = service.atualizar_status(usuario_logado, id_usuario, dados.ativo)
        status = 'ativado' if usuario.ativo else 'desativado'

        return {'mensagem': f'Usuario {usuario.nome} {status} com sucesso.'}
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


@router.patch('/{id_usuario}/resetar-senha', response_model=Mensagem)
def resetar_senha(
    usuario_logado: UsuarioLogado,
    id_usuario: int,
    dados: ResetarSenha,
    service: UsuarioServiceDep,
):
    try:
        usuario = service.resetar_senha(usuario_logado, id_usuario, dados.nova_senha)
        return {'mensagem': f'Senha de {usuario.nome} redefinida com sucesso.'}
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
