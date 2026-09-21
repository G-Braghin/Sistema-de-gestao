from src.entities.usuario import Usuario
from src.services.estoque_service import EstoqueService


class EstoqueController:
    def __init__(self, estoque_service: EstoqueService):
        self.estoque_service = estoque_service

    def dar_entrada(
        self, usuario_logado: Usuario, id_produto: int, entrada_estoque: int
    ):
        try:
            produto = self.estoque_service.dar_entrada(
                usuario_logado, id_produto, entrada_estoque
            )
            print(
                f"Entrada de {entrada_estoque} item(s) registrada com sucesso em {produto.nome}"
            )
            return produto
        except ValueError as e:
            print(f"Erro ao dar entrada no produto: {e}")
            return None

    def dar_saida(self, usuario_logado: Usuario, id_produto: int, saida_estoque: int):
        try:
            produto = self.estoque_service.dar_saida(
                usuario_logado, id_produto, saida_estoque
            )
            print(
                f"Saida de {saida_estoque} item(s) registrada com sucesso em {produto.nome}"
            )
            return produto
        except ValueError as e:
            print(f"Erro ao dar saida no produto: {e}")
            return None

    def listar_movimentacoes(self, usuario_logado: Usuario):
        try:
            movimentacoes = self.estoque_service.listar_movimentacoes(usuario_logado)
        except PermissionError as e:
            print(e)
            return None

        if not movimentacoes:
            print("Nenhuma movimentacao encontrada!")
            return []

        self.exibir_tabela(movimentacoes)
        return movimentacoes

    def exibir_tabela(self, movimentacoes: list) -> None:
        print(
            f"\n{'ID':<5}{'ID Produto':<10}{'Entrada/Saida':<18}{'Quantidade':<15}{'ID Responsavel':<15}{'Data/Hora':<25}"
        )
        print("-" * 85)
        for movimentacao in movimentacoes:
            data_formatada = movimentacao.data_hora.strftime("%d/%m/%Y %H:%M")
            print(
                f"{movimentacao.id_movimentacao:<5}{movimentacao.id_produto:<10}{movimentacao.tipo.value:<18}{movimentacao.quantidade:<15}{movimentacao.id_usuario:<15}{data_formatada:<25}"
            )
