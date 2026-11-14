from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from src.api.schemas.types import FormatarHora
from src.enums import MotivoMovimentacao, TipoMovimentacao


# Entrada
class ModificarEstoqueEntrada(BaseModel):
    quantidade: int = Field(gt=0)
    motivo: Literal[MotivoMovimentacao.AJUSTE, MotivoMovimentacao.REPOSICAO] = Field(
        description='Ajuste / Reposicao'
    )


class ModificarEstoqueSaida(BaseModel):
    quantidade: int = Field(gt=0)
    motivo: Literal[MotivoMovimentacao.AJUSTE] = Field(description='Ajuste')


# Saida
class MovimentacaoEstoque(BaseModel):
    id: int
    id_produto: int
    id_usuario: int
    quantidade: int
    tipo_movimentacao: TipoMovimentacao
    motivo: MotivoMovimentacao


class MovimentacaoListagem(MovimentacaoEstoque):
    created_at: FormatarHora
    id_venda: int | None = None


class ListarMovimentacao(BaseModel):
    movimentacoes: list[MovimentacaoListagem]
