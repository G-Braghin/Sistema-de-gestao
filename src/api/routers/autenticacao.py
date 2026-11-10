from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.api.dependencies.services import AutenticacaoServiceDep
from src.api.schemas.usuario import Token
from src.api.security import criar_token

router = APIRouter(prefix='/autenticacao', tags=['autenticacao'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/login', response_model=Token)
def login(credenciais: OAuth2Form, autenticacao: AutenticacaoServiceDep) -> Token:

    # Maneira de tratar a string de username de OAuth2 para inteiro
    try:
        id_usuario = int(credenciais.username)
    except ValueError as erro:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Credenciais inválidas.'
        ) from erro

    try:
        usuario = autenticacao.autenticar(id_usuario, credenciais.password)

        token = criar_token(usuario.id)
        return Token(access_token=token, token_type='Bearer')

    except ValueError as erro:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail=str(erro)
        ) from erro
    except PermissionError as erro:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=str(erro)
        ) from erro
