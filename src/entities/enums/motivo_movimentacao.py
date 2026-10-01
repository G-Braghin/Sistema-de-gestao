from enum import Enum


class MotivoMovimentacao(Enum):
    VENDA = 'Venda'
    CANCELAMENTO_VENDA = 'CANC. VDA'
    REPOSICAO = 'Reposicao'
    AJUSTE = 'Ajuste'