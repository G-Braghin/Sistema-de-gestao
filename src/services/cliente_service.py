import re

from src.entities.cliente import Cliente
from src.entities.enums.papel_usuario import PapelUsuario
from src.entities.usuario import Usuario
from src.repositories.cliente_repository import ClienteRepository
from src.utils.validacoes import verificar_texto_obrigatorio

CLIENTE_NAO_ATIVO = "Cliente esta desativado."
CLIENTE_NAO_ENCONTRADO = "Cliente nao encontrado."
CPF_INVALIDO = "CPF e invalido."
CPF_NAO_INSERIDO = "CPF nao pode estar vazio."


class ClienteService:
    def __init__(self, cliente_repository: ClienteRepository):
        self.cliente_repository = cliente_repository

    def _validar_cpf(self, cpf: str) -> bool:
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

    def _validar_telefone(self, telefone: str) -> bool:
        padrao = r"^[1-9]{2}9[\d]{8}$"
        return bool(re.match(padrao, telefone))

    def _buscar_cliente_ativo(self, cpf_cliente: str) -> Cliente:
        if cpf_cliente is None:
            raise ValueError(CPF_NAO_INSERIDO)

        cpf_cliente = re.sub(r"\D", "", cpf_cliente)
        if not self._validar_cpf(cpf_cliente):
            raise ValueError(CPF_INVALIDO)

        cliente = self.cliente_repository.buscar_por_cpf(cpf_cliente)

        if cliente is None:
            raise ValueError(CLIENTE_NAO_ENCONTRADO)

        if not cliente.ativo:
            raise ValueError(CLIENTE_NAO_ATIVO)

        return cliente

    def cadastrar_cliente(
        self, nome: str, cpf: str, telefone: str, endereco: str | None = None
    ) -> Cliente:

        verificar_texto_obrigatorio(nome, "O nome nao pode estar vazio.")

        if not cpf:
            raise ValueError(CPF_NAO_INSERIDO)

        cpf = re.sub(r"\D", "", cpf)

        if not self._validar_cpf(cpf):
            raise ValueError(CPF_INVALIDO)

        cliente_existente = self.cliente_repository.buscar_por_cpf(cpf)
        if cliente_existente:
            raise ValueError("O CPF já está cadastrado.")

        if not telefone:
            raise ValueError("O telefone nao pode estar vazio.")

        telefone = re.sub(r"\D", "", telefone)
        if not self._validar_telefone(telefone):
            raise ValueError("O telefone e invalido!")

        if endereco is not None:
            endereco = endereco.strip()

        novo_cliente = Cliente(
            nome=nome.strip(), cpf=cpf, telefone=telefone, endereco=endereco
        )
        return self.cliente_repository.criar(novo_cliente)

    def atualizar_telefone(self, cpf_cliente: str, telefone: str) -> Cliente:

        cliente = self._buscar_cliente_ativo(cpf_cliente)

        if not telefone:
            raise ValueError("O telefone nao pode estar vazio.")

        telefone = re.sub(r"\D", "", telefone)

        if not self._validar_telefone(telefone):
            raise ValueError("O telefone e invalido!")

        cliente.telefone = telefone
        return self.cliente_repository.atualizar(cliente)

    def atualizar_endereco(self, cpf_cliente: str, endereco: str) -> Cliente:
        cliente = self._buscar_cliente_ativo(cpf_cliente)

        if endereco is None:
            return cliente

        cliente.endereco = endereco.strip()

        return self.cliente_repository.atualizar(cliente)

    def atualizar_nome(self, cpf_cliente: str, nome: str) -> Cliente:
        cliente = self._buscar_cliente_ativo(cpf_cliente)

        verificar_texto_obrigatorio(nome, "O nome nao pode estar vazio.")

        cliente.nome = nome.strip()
        return self.cliente_repository.atualizar(cliente)

    def listar(
        self, usuario_logado: Usuario, status_ativo: bool = True
    ) -> list[Cliente]:
        if not status_ativo and usuario_logado.papel == PapelUsuario.FUNCIONARIO:
            raise PermissionError(
                "Funcionarios nao tem permissao para ver cliente desativados."
            )
        return self.cliente_repository.listar(status_ativo)

    def atualizar_status(
        self, usuario_logado: Usuario, id_cliente: int, status_ativo: bool
    ) -> Cliente:
        if usuario_logado.papel == PapelUsuario.FUNCIONARIO:
            raise PermissionError(
                "Funcionarios nao tem permissao para atualizar status de clientes."
            )

        if not id_cliente:
            raise ValueError("ID nao inserido.")

        if not isinstance(id_cliente, int) or isinstance(id_cliente, bool):
            raise TypeError("ID tem que ser um numero.")

        cliente = self.cliente_repository.buscar_por_id(id_cliente)

        if cliente is None:
            raise ValueError(CLIENTE_NAO_ENCONTRADO)

        if cliente.ativo == status_ativo:
            raise ValueError(
                "Cliente ja esta ativo."
                if status_ativo
                else "Cliente ja esta desativado."
            )
        cliente.ativo = status_ativo
        return self.cliente_repository.atualizar(cliente)
