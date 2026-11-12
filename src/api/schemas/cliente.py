from pydantic import BaseModel, Field

from src.api.schemas.types import (
    CPF,
    CPFMascara,
    NomeFormatar,
    Telefone,
    TelefoneFormatar,
)


# Entrada
class ClienteCadastro(BaseModel):
    nome: NomeFormatar = Field(min_length=3)
    cpf: CPF
    endereco: str | None = Field(default=None)
    telefone: Telefone


class ClienteAtualizar(BaseModel):
    nome: NomeFormatar | None = Field(default=None, min_length=3)
    endereco: str | None = Field(default=None, min_length=3)
    telefone: str | None = Field(default=None)


class ClienteBuscarCpf(BaseModel):
    cpf: CPF


# Resposta/Saida
class ClienteBase(BaseModel):
    id: int
    nome: NomeFormatar
    telefone: TelefoneFormatar


class ClienteListagem(ClienteBase):
    cpf: CPFMascara
    ativo: bool


class ClienteDetalhes(ClienteListagem):
    endereco: str | None = None


class ClienteListar(BaseModel):
    clientes: list[ClienteListagem]


# Filtros
class FiltroClienteListar(BaseModel):
    ativo: bool = Field(default=True)
