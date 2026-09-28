from decimal import Decimal

import pytest
from src.database.conexao import Conexao
from src.entities.produto import Produto
from src.repositories.produto_repository import ProdutoRepository


@pytest.fixture
def repository():
    conexao = Conexao()
    repository = ProdutoRepository(conexao)

    conn = conexao.get_connection()
    try:
        yield repository
    finally:
        conn.rollback()
        conn.close()



def test_criar_produto_e_buscar_id(repository):
    produto = Produto(
        nome= "TESTE_PRODUTO",
        marca="TESTE_MARCA",
        preco=10.99,
        quantidade_estoque=20 
    )
    produto_criado=repository.criar(produto)

    assert produto_criado.id_produto is not None

    produto_buscado=repository.buscar_por_id(
        produto_criado.id_produto
    )

    assert produto_buscado is not None
    assert produto_buscado.nome == "TESTE_PRODUTO"
    assert produto_buscado.marca == "TESTE_MARCA"
    assert produto_buscado.preco == Decimal("10.99")
    assert produto_buscado.quantidade_estoque == 20


def test_buscar_produto_inexistente(repository):
    produto = repository.buscar_por_id(9999999)

    assert produto is None


def test_criar_produto_permite_rollback(repository):
    produto = Produto(
        nome="TESTE_PRODUTO_ROLLBACK",
        marca="TESTE_MARCA",
        preco=Decimal("10.00"),
        quantidade_estoque=5,
    )
    repository.criar(produto)
    produto.quantidade_estoque = 8
    repository.atualizar(produto)

    conn = repository.conexao.get_connection()
    conn.rollback()

    assert repository.buscar_por_id(produto.id_produto) is None


def test_listar_produto(repository):
    produto1 = Produto(
            nome= "TESTE_PRODUTO1",
            marca="TESTE_MARCA1",
            preco=100.00,
            quantidade_estoque=20 
        )
    produto2 = Produto(
            nome= "TESTE_PRODUTO2",
            marca="TESTE_MARCA2",
            preco=100.40,
            quantidade_estoque=6 
        )

    repository.criar(produto1)
    repository.criar(produto2)

    produtos = repository.listar()

    nomes = [produto.nome for produto in produtos]

    assert "TESTE_PRODUTO1" in nomes
    assert "TESTE_PRODUTO2" in nomes


def test_atualizar_produto(repository):
    produto = Produto(
        nome="TESTE_PRODUTO",
        marca="TESTE_MARCA",
        preco=1000.00,
        quantidade_estoque=5
    )

    produto = repository.criar(produto)

    produto.nome = "TESTE_PRODUTO2"
    produto.marca = "TESTE_MARCA2"
    produto.preco = 1211.55
    produto.quantidade_estoque = 8

    resultado = repository.atualizar(produto)

    assert resultado == produto

    produto_atualizado = repository.buscar_por_id(
        produto.id_produto
    )

    assert produto_atualizado is not None
    assert produto_atualizado.nome == "TESTE_PRODUTO2"
    assert produto_atualizado.marca == "TESTE_MARCA2"
    assert produto_atualizado.preco == Decimal("1211.55")
    assert produto_atualizado.quantidade_estoque == 8

def test_atualizar_produto_inexistente(repository):
    produto = Produto(
        id_produto=9999999,
        nome="TESTE_PRODUTO",
        marca="TESTE_MARCA",
        preco=100.00,
        quantidade_estoque=1
    )

    with pytest.raises(
        ValueError,
        match="Produto com id 9999999 nao encontrado."
    ):
        repository.atualizar(produto)

