from src.entities.produto import Produto


class RelatorioEstoqueResumo:
    def __init__(
        self,
        produtos: list[Produto],
        quantidade_produtos_cadastrados: int,
        total_unidades_estoque: int,
        quantidade_produtos_sem_estoque: int,
    ) -> None:
        self.produtos = produtos
        self.quantidade_produtos_cadastrados = quantidade_produtos_cadastrados
        self.total_unidades_estoque = total_unidades_estoque
        self.quantidade_produtos_sem_estoque = quantidade_produtos_sem_estoque
