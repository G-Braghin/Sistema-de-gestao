from decimal import Decimal

from src.models import Produto
from src.repositories.produto_repository import ProdutoRepository

PRODUTO_NAO_ENCONTRADO = 'Produto nao encontrado!'
ID_INVALIDO = 'ID de produto invalido.'


class ProdutoService:
    def __init__(self, produto_repository: ProdutoRepository):
        self.produto_repository = produto_repository

    def cadastrar_produto(self, nome: str, preco: Decimal) -> Produto:

        novo_produto = Produto(
            nome=nome,
            preco=preco,
        )
        produto_criado = self.produto_repository.criar(novo_produto)

        return produto_criado

    def listar_produtos(self) -> list[Produto]:
        return self.produto_repository.listar()

    def atualizar(
        self,
        id_produto: int,
        *,
        nome: str | None = None,
        preco: Decimal | None = None,
    ) -> Produto:

        produto = self.produto_repository.buscar_por_id_para_atualizar(id_produto)
        if produto is None:
            raise LookupError(PRODUTO_NAO_ENCONTRADO)

        if nome is not None:
            produto.nome = nome

        if preco is not None:
            produto.preco = preco

        produto = self.produto_repository.atualizar(produto)

        return produto
