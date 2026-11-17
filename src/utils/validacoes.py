import re

COMPRIMENTO_CPF = 11
LIMITE_RESTO_VALIDADOR = 10
COMPRIMENTO_CELULAR = 13


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


def validar_sem_espacos(valor: str) -> str:
    if ' ' in valor:
        raise ValueError('A senha nao pode conter espacos.')
    return valor
