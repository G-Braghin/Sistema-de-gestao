from src.services.produto_service import ProdutoService


class ProdutoController:
    def __init__(self, produto_service: ProdutoService):
        self.produto_service = produto_service

    def cadastrar_produto(self, nome: str, preco):
        produto_novo = self.produto_service.cadastrar_produto(nome, preco)
        return produto_novo

    def listar_produtos(self):
        produtos = self.produto_service.listar_produtos()
        return produtos

    def atualizar_preco(self, id_produto: int, novo_preco):
        produto = self.produto_service.atualizar_preco(id_produto, novo_preco)
        return produto

    def atualizar_nome(self, id_produto: int, novo_nome: str):
        produto = self.produto_service.atualizar_nome(id_produto, novo_nome)
        return produto

    def atualizar_marca(self, id_produto: int, nova_marca: str):
        produto = self.produto_service.atualizar_marca(id_produto, nova_marca)
        return produto
