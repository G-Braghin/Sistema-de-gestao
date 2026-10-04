from decimal import Decimal


class ProdutosVendidosResumo:
    def __init__(self,id_produto:int,nome_produto:str, quantidade_vendida:int, valor_total:Decimal) -> None:
        self.id_produto = id_produto
        self.nome_produto = nome_produto
        self.quantidade_vendida = quantidade_vendida
        self.valor_total = valor_total