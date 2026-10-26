from enum import Enum


class PapelEnum(str, Enum):
    ADMIN = 'Administrador'
    GERENTE = 'Gerente'
    FUNCIONARIO = 'Funcionario'
