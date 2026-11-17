from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class RelatorioVendaResumo:
    data_inicial: date
    data_final: date
    vendas_concluidas: int
    total_periodo: Decimal
    ticket_medio: Decimal
