import re

from src.enums import PapelEnum
from src.models import Cliente, Usuario
from src.repositories.cliente_repository import ClienteRepository

CLIENTE_NAO_ATIVO = 'Cliente esta desativado.'
CLIENTE_NAO_ENCONTRADO = 'Cliente nao encontrado.'


class ClienteService:
    def __init__(self, cliente_repository: ClienteRepository):
        self.cliente_repository = cliente_repository

    def _buscar_cliente_ativo(self, id_cliente: int) -> Cliente:
        cliente = self.cliente_repository.buscar_por_id(id_cliente)

        if cliente is None:
            raise LookupError(CLIENTE_NAO_ENCONTRADO)

        if not cliente.ativo:
            raise ValueError(CLIENTE_NAO_ATIVO)

        return cliente

    def buscar_cliente_cpf(self, cpf_cliente) -> Cliente:
        cliente = self.cliente_repository.buscar_por_cpf(cpf_cliente)
        if not cliente:
            raise LookupError(CLIENTE_NAO_ENCONTRADO)

        if not cliente.ativo:
            raise ValueError(CLIENTE_NAO_ATIVO)

        return cliente

    def cadastrar_cliente(
        self, nome: str, cpf: str, telefone: str, endereco: str | None = None
    ) -> Cliente:

        cpf = re.sub(r'\D', '', cpf)

        cliente_existente = self.cliente_repository.buscar_por_cpf(cpf)
        if cliente_existente:
            raise ValueError('O CPF já está cadastrado.')

        novo_cliente = Cliente(
            nome=nome.strip(), cpf=cpf, telefone=telefone, endereco=endereco
        )
        cliente_criado = self.cliente_repository.criar(novo_cliente)

        return cliente_criado

    def atualizar(
        self,
        id_cliente: int,
        *,
        nome: str | None = None,
        telefone: str | None = None,
        endereco: str | None = None,
    ) -> Cliente:

        cliente = self._buscar_cliente_ativo(id_cliente)

        if nome is not None:
            cliente.nome = nome.strip()

        if telefone is not None:
            telefone = re.sub(r'\D', '', telefone)

            cliente.telefone = telefone

        if endereco is not None:
            cliente.endereco = endereco.strip()

        return self.cliente_repository.atualizar(cliente)

    def listar(
        self, usuario_logado: Usuario, status_ativo: bool = True
    ) -> list[Cliente]:
        if not status_ativo and usuario_logado.papel == PapelEnum.FUNCIONARIO:
            raise PermissionError(
                'Funcionarios nao tem permissao para ver cliente desativados.'
            )
        return self.cliente_repository.listar(status_ativo)

    def atualizar_status(
        self, usuario_logado: Usuario, id_cliente: int, status_ativo: bool
    ) -> Cliente:
        if usuario_logado.papel == PapelEnum.FUNCIONARIO:
            raise PermissionError(
                'Funcionarios nao tem permissao para atualizar status de clientes.'
            )

        cliente = self.cliente_repository.buscar_por_id(id_cliente)

        if cliente is None:
            raise LookupError(CLIENTE_NAO_ENCONTRADO)

        if cliente.ativo == status_ativo:
            raise ValueError(
                'Cliente ja esta ativo.'
                if status_ativo
                else 'Cliente ja esta desativado.'
            )
        cliente.ativo = status_ativo
        cliente_atualizado = self.cliente_repository.atualizar(cliente)

        return cliente_atualizado
