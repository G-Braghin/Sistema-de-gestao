from enum import Enum


class PapelEnum(str, Enum):
    ADMIN = 'Administrador'
    GERENTE = 'Gerente'
    FUNCIONARIO = 'Funcionario'


class TipoMovimentacao(str, Enum):
    ENTRADA = 'Entrada'
    SAIDA = 'Saida'


class MotivoMovimentacao(str, Enum):
    VENDA = 'Venda'
    CANCELAMENTO_VENDA = 'CANC. VDA'
    REPOSICAO = 'Reposicao'
    AJUSTE = 'Ajuste'
