from src.enums import MotivoMovimentacao
from src.models import Movimentacao
from tests.estoque.conftest import MovFactory


def test_criar_movimentacao_e_buscar_por_id(
    mov_repository, usuario_db, produto_db, mock_db_time
):
    movimentacao = MovFactory(
        id_usuario=usuario_db.id,
        id_produto=produto_db.id,
        motivo=MotivoMovimentacao.REPOSICAO,
    )

    with mock_db_time(model=Movimentacao) as hora:
        movimentacao_criada = mov_repository.criar(movimentacao)

        assert movimentacao_criada.id is not None
        assert movimentacao_criada.created_at == hora

        resultado = mov_repository.buscar_por_id(movimentacao_criada.id)

        assert resultado is not None
        assert resultado.id_produto == produto_db.id
        assert resultado.id_usuario == usuario_db.id
        assert resultado.tipo_movimentacao == movimentacao_criada.tipo_movimentacao
        assert resultado.quantidade == movimentacao_criada.quantidade
        assert resultado.created_at == hora
        assert resultado.motivo == movimentacao_criada.motivo
        assert resultado.id_venda is None


def test_buscar_movimentacao_inexistente(mov_repository):
    movimentacao = mov_repository.buscar_por_id(9999999)

    assert movimentacao is None


def test_listar_movimentacoes_retorna_lista(
    mov_repository, session, usuario_db, produto_db
):
    tamanho_esperado = 5
    movimentacoes = MovFactory.build_batch(
        tamanho_esperado, id_usuario=usuario_db.id, id_produto=produto_db.id
    )
    session.add_all(movimentacoes)

    resultado = mov_repository.listar()
    assert resultado is not None
    assert len(resultado) == len(movimentacoes)

    for mov in resultado:
        assert mov in movimentacoes


def test_listar_nenhuma_movimentacao_lista_vazia(mov_repository):
    resultado = mov_repository.listar()

    assert resultado == []
