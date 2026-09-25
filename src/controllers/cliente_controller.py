from src.services.cliente_service import ClienteService

from ..entities.cliente import Cliente


class ClienteController:
    def __init__(self, cliente_service: ClienteService):
        self.cliente_service = cliente_service

    def cadastrar_cliente(self, nome: str, cpf: str, telefone: str, endereco: str) -> Cliente:
        return self.cliente_service.cadastrar_cliente(nome, cpf, telefone, endereco)

    def atualizar_telefone(self, cpf_cliente: str, telefone_novo: str) -> Cliente:
        return self.cliente_service.atualizar_telefone(cpf_cliente, telefone_novo)

    def atualizar_endereco(self, cpf_cliente: str, endereco_novo: str) -> Cliente:
        return self.cliente_service.atualizar_endereco(cpf_cliente, endereco_novo)

    def atualizar_nome(self, cpf_cliente: str, novo_nome: str) -> Cliente:
        return self.cliente_service.atualizar_nome(cpf_cliente, novo_nome)

    def atualizar_status(self,usuario_logado, id_cliente, ativo: bool) -> Cliente:
        return self.cliente_service.atualizar_status(usuario_logado, id_cliente, ativo)
    
    def listar_clientes(self,usuario_logado, status_ativo: bool = True) -> list[Cliente]:
        return self.cliente_service.listar(usuario_logado, status_ativo)
