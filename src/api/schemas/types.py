import re
from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, PlainSerializer, StringConstraints

from src.utils.validacoes import validar_cpf, validar_telefone

REGEX_NOME = r'^[a-zA-ZÀ-ÿ0-9 ./-]+$'


def validar_cpf_schema(cpf: str) -> str:
    cpf_limpo = re.sub(r'\D', '', cpf)

    if not validar_cpf(cpf_limpo):
        raise ValueError('CPF invalido.')

    return cpf_limpo


def validar_telefone_schema(telefone: str) -> str:
    telefone_limpo = re.sub(r'\D', '', telefone)

    if not validar_telefone(telefone_limpo):
        raise ValueError('Telefone invalido.')

    return telefone_limpo


def mascarar_cpf(cpf_limpo: str) -> str:
    return f'{cpf_limpo[:3]}.***.***-{cpf_limpo[9:]}'


def formatar_telefone(telefone_limpo) -> str:
    return f'({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}'


def formatar_nome_proprio(nome: str) -> str:
    ignorar = {'da', 'de', 'do', 'das', 'dos', 'e'}
    pastes_nome = nome.lower().split()

    nome_formatado = ' '.join(
        parte if parte in ignorar and idx > 0 else parte.capitalize()
        for idx, parte in enumerate(pastes_nome)
    )

    return nome_formatado


def formatar_preco(valor: Decimal) -> str:
    valor_formatado = (
        f'{valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    )
    return f'R$ {valor_formatado}'


CPF = Annotated[str, AfterValidator(validar_cpf_schema)]
CPFMascara = Annotated[str, AfterValidator(mascarar_cpf)]
Telefone = Annotated[str, AfterValidator(validar_telefone_schema)]
TelefoneFormatar = Annotated[str, AfterValidator(formatar_telefone)]

NomeFormatar = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        pattern=REGEX_NOME,
        min_length=3,
        max_length=60,
    ),
    AfterValidator(formatar_nome_proprio),
]

Nome = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_upper=True,
        pattern=REGEX_NOME,
        min_length=3,
        max_length=60,
    ),
]

FormatarPreco = Annotated[
    Decimal, PlainSerializer(formatar_preco, return_type=str, when_used='json')
]
