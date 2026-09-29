from decimal import Decimal


class VendaItem:
    def __init__(
        self,
        id_produto: int,
        nome_produto: str,
        quantidade: int,
        preco_unitario: Decimal,
        id_venda_item: int | None = None,
        id_venda: int | None = None,
    ):
        self.id_venda_item = id_venda_item
        self.id_venda = id_venda
        self.id_produto = id_produto
        self.nome_produto = nome_produto
        self.preco_unitario = Decimal(str(preco_unitario))
        self.quantidade = quantidade
