from decimal import Decimal

from pydantic import BaseModel, Field

from src.api.schemas.types import FormatarPreco, Nome


# Entrada
class ProdutoCadastro(BaseModel):
    nome: Nome = Field(examples=['Teclado', 'Monitor'])
    preco: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class ProdutoAtualizar(BaseModel):
    nome: Nome | None = Field(default=None, examples=['Teclado', 'Monitor'])
    preco: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)


# Resposta/Saida
class ProdutoInfo(BaseModel):
    id: int
    nome: str
    preco: FormatarPreco
    quantidade: int


class ListarProdutos(BaseModel):
    produtos: list[ProdutoInfo]
