from src.services.produto_service import ProdutoService


class ProdutoController:
    def __init__(self, produto_service: ProdutoService):
        self.produto_service = produto_service

    def cadastrar_produto(self, nome: str, marca: str, preco):
        try:
            produto_novo = self.produto_service.cadastrar_produto(nome, marca, preco)
            print(
                f"{produto_novo.nome} cadastrado com sucesso! ID: {produto_novo.id_produto}"
            )
            return produto_novo
        except ValueError as e:
            print(f"Erro ao cadastrar produto: {e}")
            return None

    def listar_produtos(self):
        produtos = self.produto_service.listar_produtos()
        if not produtos:
            print("Nenhum produto encontrado!")
            return []

        self.exibir_tabela(produtos)
        return produtos

    def atualizar_preco(self, id_produto: int, novo_preco):
        try:
            produto = self.produto_service.atualizar_preco(id_produto, novo_preco)
            print(f"Preco de {produto.nome} atualizou para $ {produto.preco}")
            return produto
        except ValueError as e:
            print(f"Erro ao atualizar preco: {e}")
            return None

    def atualizar_nome(self, id_produto: int, novo_nome: str):
        try:
            produto = self.produto_service.atualizar_nome(id_produto, novo_nome)
            print(f"Nome atualizado para {produto.nome}")
            return produto
        except ValueError as e:
            print(f"Erro ao atualizar nome: {e}")
            return None

    def atualizar_marca(self, id_produto: int, nova_marca: str):
        try:
            produto = self.produto_service.atualizar_marca(id_produto, nova_marca)
            print(f"Marca atualizada para {produto.marca}")
            return produto
        except ValueError as e:
            print(f"Erro ao atualizar marca: {e}")
            return None

    def exibir_tabela(self, produtos: list) -> None:
        print(f"\n{'ID':<5}{'Nome':<20}{'Marca':<15}{'Preco':>10}{'Estoque':>10}")
        print("-" * 65)
        for p in produtos:
            print(
                f"{p.id_produto:<5}{p.nome:<20}{p.marca:<15}{p.preco:>10}{p.quantidade_estoque:>9}"
            )
