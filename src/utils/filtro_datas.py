from enum import Enum


class FiltroDatas(Enum):
    HOJE = 'Hoje'
    ONTEM = 'Ontem'
    ULTIMOS_7_DIAS = 'Últimos 7 dias'
    ULTIMOS_30_DIAS = 'Últimos 30 dias'
    MES_ATUAL = 'Mês atual'
    MES_ANTERIOR = 'Mês anterior'
    ANO_ATUAL = 'Ano atual'
    ANO_ANTERIOR = 'Ano anterior'
    PERSONALIZADO = 'Personalizado' 