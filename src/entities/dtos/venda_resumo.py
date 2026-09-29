from datetime import datetime
from decimal import Decimal

from src.entities.enums.status_venda import StatusVenda


class VendaResumo:
    def __init__(
        self,
        id_venda: int,
        nome_cliente: str,
        nome_vendedor: str,
        data_venda: datetime,
        valor_total: Decimal,
        status: StatusVenda,
    ):
        self.id_venda = id_venda
        self.nome_cliente = nome_cliente
        self.nome_vendedor = nome_vendedor
        self.data_venda = data_venda
        self.valor_total = valor_total
        self.status = status
