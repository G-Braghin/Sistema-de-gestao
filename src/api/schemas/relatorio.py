from datetime import datetime

from pydantic import BaseModel, Field

from src.api.schemas.produto import ProdutoInfo
from src.api.schemas.types import FormatarHoraLocal, FormatarPreco


# Entrada
class RelatorioData(BaseModel):
    inicio: datetime
    fim: datetime


# Saida


class RelatorioVendaRes(BaseModel):
    data_inicial: FormatarHoraLocal
    data_final: FormatarHoraLocal
    vendas_concluidas: int
    total_periodo: FormatarPreco
    ticket_medio: FormatarPreco


class ProdutosMaisVendidos(BaseModel):
    id_produto: int
    nome_produto: str
    quantidade_vendida: int
    valor_total: FormatarPreco


class ListaProdutosVendidos(BaseModel):
    produtos: list[ProdutosMaisVendidos]


class RelatorioEstoqueRes(BaseModel):
    produtos: list[ProdutoInfo]
    quantidade_produtos_cadastrados: int
    total_unidades_estoque: int
    quantidade_produtos_sem_estoque: int


class EstoqueFiltro(BaseModel):
    limite: int = Field(gt=0)
