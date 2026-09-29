from enum import Enum


class MotivoMovimentacao(Enum):
    VENDA = 'Venda'
    CANCELAMENTO_VENDA = 'Cancelamento de Venda'
    REPOSICAO = 'Reposicao'
    AJUSTE = 'Ajuste'