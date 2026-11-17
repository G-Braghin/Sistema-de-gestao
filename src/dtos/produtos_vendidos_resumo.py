from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ProdutosVendidosResumo:
    id_produto: int
    nome_produto: str
    quantidade_vendida: int
    valor_total: Decimal
