from src.entities.usuario import Usuario
from src.services.estoque_service import EstoqueService


class EstoqueController:
    def __init__(self, estoque_service: EstoqueService):
        self.estoque_service = estoque_service

    def dar_entrada(
        self, usuario_logado: Usuario, id_produto: int, entrada_estoque: int, motivo
    ):
        produto = self.estoque_service.dar_entrada(
            usuario_logado, id_produto, entrada_estoque, motivo
        )
        return produto

    def dar_saida(
        self, usuario_logado: Usuario, id_produto: int, saida_estoque: int, motivo
    ):
        produto = self.estoque_service.dar_saida(
            usuario_logado, id_produto, saida_estoque, motivo
        )
        return produto

    def listar_movimentacoes(self, usuario_logado: Usuario):
        movimentacoes = self.estoque_service.listar_movimentacoes(usuario_logado)
        return movimentacoes

    def relatorio_estoque(self, usuario_logado):
        relatorio = self.estoque_service.relatorio_estoque(usuario_logado)
        return relatorio

    def relatorio_estoque_baixo(self, usuario_logado, limite):
        relatorio = self.estoque_service.relatorio_estoque_baixo(usuario_logado, limite)
        return relatorio
