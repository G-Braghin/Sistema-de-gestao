from pydantic import BaseModel, Field

from src.enums import PapelEnum


class Token(BaseModel):
    access_token: str
    token_type: str


class UsuarioPublico(BaseModel):
    id: int
    nome: str
    papel: PapelEnum
    ativo: bool


class UsuarioCadastro(BaseModel):
    nome: str = Field(min_length=3, max_length=60)
    papel: PapelEnum = Field(default=PapelEnum.FUNCIONARIO)
    senha: str = Field(min_length=3)


class UsuarioLista(BaseModel):
    usuarios: list[UsuarioPublico]


class FiltroListarUsuario(BaseModel):
    ativo: bool = Field(default=True)


class AtualizarSenha(BaseModel):
    senha_atual: str = Field(min_length=3)
    nova_senha: str = Field(min_length=3)


class Mensagem(BaseModel):
    mensagem: str


class AtualizarStatus(BaseModel):
    ativo: bool


class ResetarSenha(BaseModel):
    nova_senha: str = Field(min_length=3)
