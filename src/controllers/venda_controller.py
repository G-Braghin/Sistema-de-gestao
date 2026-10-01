from src.entities.enums.status_venda import StatusVenda
from src.services.venda_service import VendaService


class VendaController:
    def __init__(self, venda_service: VendaService):
        self.venda_service = venda_service

    def realizar_venda(self, usuario_logado, id_cliente, itens):
        venda = self.venda_service.realizar_venda(usuario_logado, id_cliente, itens)
        return venda

    def realizar_cancelamento(self, usuario_logado, id_venda):
        venda_cancelada = self.venda_service.cancelar_venda(usuario_logado, id_venda)
        return venda_cancelada

    def listar_resumo(self, usuario_logado, status_venda: StatusVenda | None = None):
        venda_resumo = self.venda_service.listar_resumo(usuario_logado, status_venda)
        return venda_resumo

    def listar_venda(self, usuario_logado, id_venda):
        venda = self.venda_service.listar_venda_itens(usuario_logado, id_venda)
        return venda
