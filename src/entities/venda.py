from datetime import datetime, timezone
from decimal import Decimal

from src.entities.enums.status_venda import StatusVenda
from src.entities.venda_item import VendaItem


class Venda:
    def __init__(
        self,
        id_cliente: int,
        id_usuario: int,
        itens: list[VendaItem],
        preco_total: Decimal,
        status: StatusVenda,
        id_venda: int | None = None,
        data_hora: datetime | None = None,
        data_cancelamento: datetime | None = None,
        id_usuario_cancelamento: int | None = None,
    ):
        self.id_venda = id_venda
        self.id_cliente = id_cliente
        self.id_usuario = id_usuario
        self.itens = itens
        self.preco_total = Decimal(str(preco_total))
        self.data_hora = (
            data_hora if data_hora is not None else datetime.now(timezone.utc)
        )
        self.status = status
        self.data_cancelamento = data_cancelamento
        self.id_usuario_cancelamento = id_usuario_cancelamento
