import re

COMPRIMENTO_CPF = 11
LIMITE_RESTO_VALIDADOR = 10
COMPRIMENTO_CELULAR = 13


def verificar_id(id_registro: int, mensagem: str = 'ID invalido.') -> None:
    if not isinstance(id_registro, int) or isinstance(id_registro, bool):
        raise TypeError('ID tem que ser um numero inteiro.')

    if id_registro <= 0:
        raise ValueError(mensagem)


def verificar_texto_obrigatorio(texto: str | None, mensagem: str) -> None:
    if not texto or not texto.strip():
        raise ValueError(mensagem)


def validar_cpf(cpf: str) -> bool:
    if len(cpf) != COMPRIMENTO_CPF:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    digito1 = 0 if resto == LIMITE_RESTO_VALIDADOR else resto

    if digito1 != int(cpf[9]):
        return False

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    digito2 = 0 if resto == LIMITE_RESTO_VALIDADOR else resto

    return digito2 == int(cpf[10])


def validar_telefone(telefone: str) -> bool:
    if len(telefone) == COMPRIMENTO_CELULAR and telefone.startswith('55'):
        telefone = telefone[2:]

    padrao = r'^[1-9]{2}9[\d]{8}$'

    return bool(re.match(padrao, telefone))
