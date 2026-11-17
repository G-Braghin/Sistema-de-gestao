from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.utils.fuso import FUSO_HORARIO


def mascarar_cpf(cpf_limpo: str) -> str:
    return f'{cpf_limpo[:3]}.***.***-{cpf_limpo[9:]}'


def formatar_telefone(telefone_limpo: str) -> str:
    return f'({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}'


def formatar_nome_proprio(nome: str) -> str:
    ignorar = {'da', 'de', 'do', 'das', 'dos', 'e'}
    partes_nome = nome.lower().split()

    return ' '.join(
        parte if parte in ignorar and idx > 0 else parte.capitalize()
        for idx, parte in enumerate(partes_nome)
    )


def formatar_preco(valor: Decimal) -> str:
    valor_formatado = (
        f'{valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    )
    return f'R$ {valor_formatado}'


def formatar_hora_db(hora: datetime) -> str:
    if hora.tzinfo is None:
        hora = hora.replace(tzinfo=ZoneInfo('UTC'))

    data_formatada = hora.astimezone(FUSO_HORARIO).strftime('%d/%m/%Y %H:%M')
    return data_formatada


def formatar_hora_local(hora: datetime) -> str:
    return hora.strftime('%d/%m/%Y %H:%M')
