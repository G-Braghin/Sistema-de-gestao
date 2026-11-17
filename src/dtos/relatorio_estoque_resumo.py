from dataclasses import dataclass

from src.models import Produto


@dataclass
class RelatorioEstoqueResumo:
    produtos: list[Produto]
    quantidade_produtos_cadastrados: int
    total_unidades_estoque: int
    quantidade_produtos_sem_estoque: int
