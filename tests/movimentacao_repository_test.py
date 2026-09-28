from decimal import Decimal

import pytest
from src.database.conexao import Conexao
from src.entities.enums.papel_usuario import PapelUsuario
from src.entities.enums.tipo_movimentacao import TipoMovimentacao
from src.entities.movimentacao_estoque import MovimentacaoEstoque
from src.entities.produto import Produto
from src.entities.usuario import Usuario
from src.repositories.movimentacao_repository import MovimentacaoRepository
from src.repositories.produto_repository import ProdutoRepository


@pytest.fixture
def repositories():
    conexao = Conexao()
    conn = conexao.get_connection()
    movimentacao_repository = MovimentacaoRepository(conexao)
    produto_repository = ProdutoRepository(conexao)

    try:
        produto = Produto(
            nome="TESTE_PRODUTO_MOVIMENTACAO",
            marca="TESTE_MARCA",
            preco=Decimal("100.00"),
            quantidade_estoque=10,
        )
        produto = produto_repository.criar(produto)

        usuario = Usuario(
            nome="TESTE_USUARIO_MOVIMENTACAO",
            senha_hash="teste_hash",
            papel=PapelUsuario.FUNCIONARIO,
            ativo=True,
        )

        # O repository de usuario ainda faz commit; aqui mantemos tudo sem commit.
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO usuarios (nome, senha_hash, papel, ativo)
                VALUES (%s, %s, %s, %s)
                RETURNING id_usuario
                """,
                (usuario.nome, usuario.senha_hash, usuario.papel.value, usuario.ativo),
            )
            usuario.id_usuario = cursor.fetchone()[0]

        yield {
            "movimentacao": movimentacao_repository,
            "produto_repository": produto_repository,
            "produto": produto,
            "usuario": usuario,
            "conexao": conexao,
        }
    finally:
        conn.rollback()
        conn.close()


def test_criar_movimentacao_e_buscar_por_id(repositories):
    repository = repositories["movimentacao"]
    produto = repositories["produto"]
    usuario = repositories["usuario"]

    movimentacao = MovimentacaoEstoque(
        id_produto=produto.id_produto,
        id_usuario=usuario.id_usuario,
        tipo=TipoMovimentacao.ENTRADA,
        quantidade=5,
    )

    movimentacao_criada = repository.criar(movimentacao)

    assert movimentacao_criada.id_movimentacao is not None

    movimentacao_buscada = repository.buscar_por_id(movimentacao_criada.id_movimentacao)

    assert movimentacao_buscada is not None
    assert movimentacao_buscada.id_produto == produto.id_produto
    assert movimentacao_buscada.id_usuario == usuario.id_usuario
    assert movimentacao_buscada.tipo == TipoMovimentacao.ENTRADA
    assert movimentacao_buscada.quantidade == 5
    assert movimentacao_buscada.data_hora is not None


def test_buscar_movimentacao_inexistente(repositories):
    repository = repositories["movimentacao"]

    movimentacao = repository.buscar_por_id(9999999)

    assert movimentacao is None


def test_produto_e_movimentacao_permitem_rollback(repositories):
    repository = repositories["movimentacao"]
    produto_repository = repositories["produto_repository"]
    produto = repositories["produto"]
    usuario = repositories["usuario"]

    produto.quantidade_estoque += 5
    produto_repository.atualizar(produto)
    movimentacao = MovimentacaoEstoque(
        id_produto=produto.id_produto,
        id_usuario=usuario.id_usuario,
        tipo=TipoMovimentacao.ENTRADA,
        quantidade=5,
    )
    repository.criar(movimentacao)

    conn = repositories["conexao"].get_connection()
    conn.rollback()

    assert repository.buscar_por_id(movimentacao.id_movimentacao) is None
    assert produto_repository.buscar_por_id(produto.id_produto) is None


def test_listar_movimentacoes(repositories):
    repository = repositories["movimentacao"]
    produto = repositories["produto"]
    usuario = repositories["usuario"]

    movimentacao1 = MovimentacaoEstoque(
        id_produto=produto.id_produto,
        id_usuario=usuario.id_usuario,
        tipo=TipoMovimentacao.ENTRADA,
        quantidade=10,
    )

    movimentacao2 = MovimentacaoEstoque(
        id_produto=produto.id_produto,
        id_usuario=usuario.id_usuario,
        tipo=TipoMovimentacao.SAIDA,
        quantidade=3,
    )

    repository.criar(movimentacao1)
    repository.criar(movimentacao2)

    movimentacoes = repository.listar()

    ids = [movimentacao.id_movimentacao for movimentacao in movimentacoes]

    assert movimentacao1.id_movimentacao in ids
    assert movimentacao2.id_movimentacao in ids


def test_criar_movimentacao_de_saida(repositories):
    repository = repositories["movimentacao"]
    produto = repositories["produto"]
    usuario = repositories["usuario"]

    movimentacao = MovimentacaoEstoque(
        id_produto=produto.id_produto,
        id_usuario=usuario.id_usuario,
        tipo=TipoMovimentacao.SAIDA,
        quantidade=3,
    )

    movimentacao_criada = repository.criar(movimentacao)

    assert movimentacao_criada.id_movimentacao is not None
    assert movimentacao_criada.tipo == TipoMovimentacao.SAIDA
    assert movimentacao_criada.quantidade == 3
