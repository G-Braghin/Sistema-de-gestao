import re
from decimal import Decimal, InvalidOperation

from src.entities.produto import Produto
from src.repositories.produto_repository import ProdutoRepository

PRODUTO_NAO_ENCONTRADO= "Produto nao encontrado!"
class ProdutoService:
    def __init__(self, produto_repository: ProdutoRepository):
        self.produto_repository = produto_repository

    def validar_nome(self, nome:str) -> bool:
        nome = nome.strip()
        if not 3 <= len(nome) <= 60:
            return False

        regex_caracteres_validos = (
        r"^[a-zA-Z0-9áàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ\s.\-/]+$"
        )
        if not re.match(regex_caracteres_validos, nome):
            return False

        return True

    def validar_preco(self, preco:str | float) -> bool:
        try:
            preco = Decimal(str(preco))
        except (InvalidOperation, ValueError, TypeError):
            return False
        
        if preco <= 0 :
            return False

        if preco.as_tuple().exponent < -2:
            return False

        return True


    def cadastrar_produto(self, nome:str, marca:str, preco) -> Produto:
        if not self.validar_nome(nome):
            raise ValueError("O nome do produto e invalido!")

        if not self.validar_nome(marca):
            raise ValueError("A marca do produto e invalida!")

        if not self.validar_preco(preco):
            raise ValueError("O preco do produto e invalido!")

        novo_produto = Produto(
            nome=nome.strip().upper(),
            marca=marca.strip().upper(),
            preco=Decimal(str(preco)),
        )
        return self.produto_repository.criar(novo_produto)


    def listar_produtos(self) -> list[Produto]:
        return self.produto_repository.listar()


    def atualizar_preco(self, id_produto:int, preco) -> Produto:
        produto = self.produto_repository.buscar_por_id(id_produto)
        if produto is None:
            raise ValueError(PRODUTO_NAO_ENCONTRADO)

        if not self.validar_preco(preco):
            raise ValueError("O preco do produto e invalido!")
        produto.preco = Decimal(str(preco))

        return self.produto_repository.atualizar(produto)


    def atualizar_nome(self, id_produto:int, nome:str) -> Produto:
        produto= self.produto_repository.buscar_por_id(id_produto)
        if produto is None:
            raise ValueError(PRODUTO_NAO_ENCONTRADO)

        if not self.validar_nome(nome):
            raise ValueError("O nome do produto e invalido!")
        produto.nome = nome.strip().upper()

        return self.produto_repository.atualizar(produto)


    def atualizar_marca(self, id_produto:int, marca:str) -> Produto:
        produto= self.produto_repository.buscar_por_id(id_produto)
        if produto is None:
            raise ValueError(PRODUTO_NAO_ENCONTRADO)
    
        if not self.validar_nome(marca):
            raise ValueError("A marca do produto e invalida!")
        produto.marca = marca.strip().upper()
    
        return self.produto_repository.atualizar(produto)


