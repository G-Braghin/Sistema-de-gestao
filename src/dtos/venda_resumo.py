from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.enums import StatusVenda


@dataclass
class VendaResumo:
    id_venda: int
    nome_cliente: str
    nome_vendedor: str
    data_venda: datetime
    valor_total: Decimal
    status: StatusVenda
