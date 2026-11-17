from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, Field, PlainSerializer, StringConstraints

from src.utils.formatadores import (
    formatar_hora_db,
    formatar_hora_local,
    formatar_nome_proprio,
    formatar_preco,
    formatar_telefone,
    mascarar_cpf,
)
from src.utils.validacoes import (
    validar_cpf_schema,
    validar_sem_espacos,
    validar_telefone_schema,
)

REGEX_NOME = r'^[a-zA-ZÀ-ÿ0-9 ./-]+$'

CPF = Annotated[str, AfterValidator(validar_cpf_schema)]
Telefone = Annotated[str, AfterValidator(validar_telefone_schema)]
TelefoneFormatar = Annotated[str, AfterValidator(formatar_telefone)]

NomeFormatar = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        pattern=REGEX_NOME,
        min_length=3,
        max_length=120,
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
        max_length=100,
    ),
]

SenhaValida = Annotated[
    str,
    Field(min_length=3, max_length=60),
    AfterValidator(validar_sem_espacos),
]

CPFMascara = Annotated[
    str, PlainSerializer(mascarar_cpf, return_type=str, when_used='json')
]

FormatarPreco = Annotated[
    Decimal, PlainSerializer(formatar_preco, return_type=str, when_used='json')
]

FormatarHora = Annotated[
    datetime, PlainSerializer(formatar_hora_db, return_type=str, when_used='json')
]

FormatarHoraLocal = Annotated[
    datetime, PlainSerializer(formatar_hora_local, return_type=str, when_used='json')
]
