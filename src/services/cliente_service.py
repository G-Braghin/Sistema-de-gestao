import re

from src.enums import PapelEnum
from src.models import Cliente, Usuario
from src.repositories.cliente_repository import ClienteRepository
from src.utils.validacoes import (
    validar_cpf,
    validar_telefone,
    verificar_texto_obrigatorio,
)

CLIENTE_NAO_ATIVO = 'Cliente esta desativado.'
CLIENTE_NAO_ENCONTRADO = 'Cliente nao encontrado.'
CPF_INVALIDO = 'CPF e invalido.'
CPF_NAO_INSERIDO = 'CPF nao pode estar vazio.'
COMPRIMENTO_CPF = 11
COMPRIMENTO_CELULAR = 13
LIMITE_RESTO_VALIDADOR = 10


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

    def buscar_cliente_cpf(self, cpf_cliente):
        cliente = self.cliente_repository.buscar_por_cpf(cpf_cliente)
        if not cliente:
            raise LookupError(CLIENTE_NAO_ENCONTRADO)

        if not cliente.ativo:
            raise ValueError(CLIENTE_NAO_ATIVO)

        return cliente

    def cadastrar_cliente(
        self, nome: str, cpf: str, telefone: str, endereco: str | None = None
    ) -> Cliente:

        verificar_texto_obrigatorio(nome, 'O nome nao pode estar vazio.')

        if not cpf:
            raise ValueError(CPF_NAO_INSERIDO)

        cpf = re.sub(r'\D', '', cpf)

        if not validar_cpf(cpf):
            raise ValueError(CPF_INVALIDO)

        cliente_existente = self.cliente_repository.buscar_por_cpf(cpf)
        if cliente_existente:
            raise ValueError('O CPF já está cadastrado.')

        if not telefone:
            raise ValueError('O telefone nao pode estar vazio.')

        telefone = re.sub(r'\D', '', telefone)
        if not validar_telefone(telefone):
            raise ValueError('O telefone e invalido!')

        if endereco is not None:
            endereco = endereco.strip()

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
            verificar_texto_obrigatorio(nome, 'O nome nao pode estar vazio.')
            cliente.nome = nome.strip()

        if telefone is not None:
            telefone = re.sub(r'\D', '', telefone)

            if not validar_telefone(telefone):
                raise ValueError('Telefone invalido.')

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

        if not id_cliente:
            raise ValueError('ID nao inserido.')

        if not isinstance(id_cliente, int) or isinstance(id_cliente, bool):
            raise TypeError('ID tem que ser um numero.')

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
