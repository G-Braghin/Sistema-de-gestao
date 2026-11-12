from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from src.api.dependencies.autenticacao import UsuarioLogado
from src.api.dependencies.services import UsuarioServiceDep
from src.api.schemas.common import Mensagem
from src.api.schemas.usuario import (
    AtualizarSenha,
    FiltroListarUsuario,
    UsuarioCadastro,
    UsuarioLista,
    UsuarioPublico,
)
from src.models import Usuario

router = APIRouter(prefix='/usuarios', tags=['usuarios'])


@router.post('/cadastro', response_model=UsuarioPublico, status_code=HTTPStatus.CREATED)
def cadastrar_usuario(
    usuario_logado: UsuarioLogado,
    dados_cadastro: UsuarioCadastro,
    service: UsuarioServiceDep,
):
    try:
        dados_dict = dados_cadastro.model_dump()
        usuario_db = Usuario(**dados_dict)

        novo_usuario = service.cadastrar_usuario(usuario_logado, usuario_db)

        return novo_usuario
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro


@router.get('/listar', response_model=UsuarioLista)
def listar_usuario(
    usuario_logado: UsuarioLogado,
    filtro_usuario: Annotated[FiltroListarUsuario, Query()],
    service: UsuarioServiceDep,
):
    try:
        usuarios = service.listar_usuarios(usuario_logado, filtro_usuario.ativo)

        return {'usuarios': usuarios}
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro


@router.patch('/atualizar-senha', response_model=Mensagem)
def atualizar_propria_senha(
    usuario_logado: UsuarioLogado,
    dados_senha: AtualizarSenha,
    service: UsuarioServiceDep,
):
    try:
        service.atualizar_senha_usuario(
            usuario_logado, dados_senha.senha_atual, dados_senha.nova_senha
        )
        return {'mensagem': 'Senha atualizada com sucesso.'}
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
