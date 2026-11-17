from pydantic import BaseModel, Field

from src.api.schemas.types import NomeFormatar, SenhaValida
from src.enums import PapelEnum


class Token(BaseModel):
    access_token: str
    token_type: str


# Entrada
class UsuarioCadastro(BaseModel):
    nome: NomeFormatar = Field(examples=['Bob'])
    papel: PapelEnum = Field(default=PapelEnum.FUNCIONARIO)
    senha: SenhaValida


class AtualizarSenha(BaseModel):
    senha_atual: SenhaValida
    nova_senha: SenhaValida


class FiltroListarUsuario(BaseModel):
    ativo: bool = Field(default=True)


class ResetarSenha(BaseModel):
    nova_senha: SenhaValida


# Saida
class UsuarioPublico(BaseModel):
    id: int
    nome: str
    papel: PapelEnum
    ativo: bool


class UsuarioLista(BaseModel):
    usuarios: list[UsuarioPublico]
