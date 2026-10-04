from datetime import date
from decimal import Decimal


class RelatorioVendaResumo:
    def __init__(
        self,
        data_inicial: date,
        data_final: date,
        vendas_concluidas: int,
        total_periodo: Decimal,
        ticket_medio: Decimal,
    ):
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.vendas_concluidas = vendas_concluidas
        self.total_periodo = total_periodo
        self.ticket_medio = ticket_medio

