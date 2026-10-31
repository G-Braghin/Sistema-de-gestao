import re
from decimal import Decimal, InvalidOperation

from src.models import Produto
from src.repositories.produto_repository import ProdutoRepository
from src.utils.validacoes import verificar_id

PRODUTO_NAO_ENCONTRADO = 'Produto nao encontrado!'
ID_INVALIDO = 'ID de produto invalido.'


class ProdutoService:
    def __init__(self, produto_repository: ProdutoRepository):
        self.produto_repository = produto_repository

    @staticmethod
    def validar_nome(nome: str) -> bool:
        min_length = 3
        max_length = 60

        if not isinstance(nome, str):
            return False

        nome = nome.strip()
        if not min_length <= len(nome) <= max_length:
            return False

        regex_caracteres_validos = r'[a-zA-Z0-9áàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ .\-/]+'
        return re.fullmatch(regex_caracteres_validos, nome) is not None

    @staticmethod
    def validar_preco(preco: str | float | Decimal) -> bool:
        try:
            preco = Decimal(str(preco))
        except InvalidOperation, ValueError, TypeError:
            return False

        if not preco.is_finite():
            return False

        if preco <= 0:
            return False

        return preco.as_tuple().exponent >= -2

    def cadastrar_produto(self, nome: str, preco) -> Produto:
        if not self.validar_nome(nome):
            raise ValueError('O nome do produto e invalido!')

        if not self.validar_preco(preco):
            raise ValueError('O preco do produto e invalido!')

        novo_produto = Produto(
            nome=nome.strip().upper(),
            preco=Decimal(str(preco)),
        )
        produto_criado = self.produto_repository.criar(novo_produto)

        return produto_criado

    def listar_produtos(self) -> list[Produto]:
        return self.produto_repository.listar()

    def atualizar_preco(self, id_produto: int, preco) -> Produto:
        verificar_id(id_produto, ID_INVALIDO)

        if not self.validar_preco(preco):
            raise ValueError('O preco do produto e invalido!')

        produto = self.produto_repository.buscar_por_id_para_atualizar(id_produto)
        if produto is None:
            raise ValueError(PRODUTO_NAO_ENCONTRADO)

        produto.preco = Decimal(str(preco))
        produto = self.produto_repository.atualizar(produto)

        return produto

    def atualizar_nome(self, id_produto: int, nome: str) -> Produto:
        verificar_id(id_produto, ID_INVALIDO)

        if not self.validar_nome(nome):
            raise ValueError('O nome do produto e invalido!')

        produto = self.produto_repository.buscar_por_id_para_atualizar(id_produto)
        if produto is None:
            raise ValueError(PRODUTO_NAO_ENCONTRADO)

        produto.nome = nome.strip().upper()
        produto = self.produto_repository.atualizar(produto)

        return produto
