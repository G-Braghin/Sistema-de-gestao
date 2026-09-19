import re

from src.entities.cliente import Cliente
from src.repositories.cliente_repository import ClienteRepository


class ClienteService:
    def __init__(self, cliente_repository: ClienteRepository):
        self.cliente_repository = cliente_repository

    def validar_cpf(self, cpf: str) -> bool:
        if len(cpf) != 11:
            return False

        if cpf == cpf[0] * 11:
            return False

        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = (soma * 10) % 11
        digito1 = 0 if resto == 10 else resto

        if digito1 != int(cpf[9]):
            return False

        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = (soma * 10) % 11
        digito2 = 0 if resto == 10 else resto

        return digito2 == int(cpf[10])

    def validar_telefone(self, telefone: str) -> bool:
        padrao = r"^[1-9]{2}9[\d]{8}$"
        return bool(re.match(padrao, telefone))

    def cadastrar_cliente(
        self, nome: str, cpf: str, telefone: str, endereco: str | None = None
    ) -> Cliente:
        cpf = re.sub(r"\D", "", cpf)
        telefone = re.sub(r"\D", "", telefone)

        if not nome.strip():
            raise ValueError("O nome nao pode estar vazio.")

        if not cpf:
            raise ValueError("O CPF nao pode estar vazio.")

        if not self.validar_cpf(cpf):
            raise ValueError("O CPF e invalido!")

        cliente_existente = self.cliente_repository.buscar_por_cpf(cpf)
        if cliente_existente:
            raise ValueError("O CPF já está cadastrado.")

        if not telefone:
            raise ValueError("O telefone nao pode estar vazio.")

        if not self.validar_telefone(telefone):
            raise ValueError("O telefone e invalido!")

        if endereco is not None:
            endereco = endereco.strip()

        novo_cliente = Cliente(
            nome=nome.strip(), cpf=cpf, telefone=telefone, endereco=endereco
        )
        return self.cliente_repository.criar(novo_cliente)

    def atualizar_telefone(self, cpf_cliente: str, telefone: str) -> Cliente:
        cliente = self.cliente_repository.buscar_por_cpf(cpf_cliente)
        if cliente is None:
            raise ValueError("Cliente nao encontrado.")

        telefone = re.sub(r"\D", "", telefone)
        if not telefone:
            raise ValueError("O telefone nao pode estar vazio.")

        if not self.validar_telefone(telefone):
            raise ValueError("O telefone e invalido!")

        cliente.telefone = telefone
        return self.cliente_repository.atualizar(cliente)

    def atualizar_endereco(self, cpf_cliente: str, endereco: str) -> Cliente:
        cliente = self.cliente_repository.buscar_por_cpf(cpf_cliente)
        if cliente is None:
            raise ValueError("Cliente nao encontrado.")

        if endereco is None:
            return cliente

        cliente.endereco = endereco.strip()

        return self.cliente_repository.atualizar(cliente)
