from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from src.database.conexao import Conexao
from src.entities.dtos.venda_resumo import VendaResumo
from src.entities.enums.papel_usuario import PapelUsuario
from src.entities.enums.status_venda import StatusVenda
from src.entities.produto import Produto
from src.entities.venda import Venda
from src.entities.venda_item import VendaItem
from src.repositories.produto_repository import ProdutoRepository
from src.repositories.venda_repository import VendaRepository


@pytest.fixture
def dados():
    conexao = Conexao()
    conn = conexao.get_connection()
    try:
        # SQL direto evita os commits dos repositories de cliente e usuario.
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO clientes (nome, cpf, telefone, endereco, ativo)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_cliente
                """,
                (
                    "TESTE_CLIENTE_VENDA",
                    str(uuid4().int % 100000000000).zfill(11),
                    "11999999999",
                    "TESTE_ENDERECO",
                    True,
                ),
            )
            id_cliente = cursor.fetchone()[0]
            cursor.execute(
                """
                INSERT INTO usuarios (nome, senha_hash, papel, ativo)
                VALUES (%s, %s, %s, %s)
                RETURNING id_usuario
                """,
                (
                    "TESTE_USUARIO_VENDA",
                    "teste_hash",
                    PapelUsuario.ADMINISTRADOR.value,
                    True,
                ),
            )
            id_usuario = cursor.fetchone()[0]

        produto_repository = ProdutoRepository(conexao)
        teclado = produto_repository.criar(
            Produto(nome="TESTE_TECLADO", marca="TESTE_MARCA", preco="100.00")
        )
        mouse = produto_repository.criar(
            Produto(nome="TESTE_MOUSE", marca="TESTE_MARCA", preco="25.00")
        )

        yield {
            "repository": VendaRepository(conexao),
            "conn": conn,
            "id_cliente": id_cliente,
            "id_usuario": id_usuario,
            "teclado": teclado,
            "mouse": mouse,
        }
    finally:
        conn.rollback()
        conn.close()


@pytest.fixture
def venda(dados):
    teclado = dados["teclado"]
    mouse = dados["mouse"]
    return Venda(
        id_cliente=dados["id_cliente"],
        id_usuario=dados["id_usuario"],
        itens=[
            VendaItem(
                id_produto=teclado.id_produto,
                nome_produto=teclado.nome,
                quantidade=1,
                preco_unitario=teclado.preco,
            ),
            VendaItem(
                id_produto=mouse.id_produto,
                nome_produto=mouse.nome,
                quantidade=2,
                preco_unitario=mouse.preco,
            ),
        ],
        preco_total=Decimal("150.00"),
        status=StatusVenda.CONCLUIDO,
    )


def test_criar_venda_e_buscar_por_id(dados, venda):
    repository = dados["repository"]
    resultado = repository.criar(venda)

    assert resultado is venda
    assert venda.id_venda is not None
    assert all(item.id_venda_item is not None for item in venda.itens)
    assert all(item.id_venda == venda.id_venda for item in venda.itens)

    buscada = repository.buscar_por_id(venda.id_venda)

    assert buscada is not None
    assert buscada.id_cliente == venda.id_cliente
    assert buscada.id_usuario == venda.id_usuario
    assert buscada.preco_total == Decimal("150.00")
    assert buscada.data_hora == venda.data_hora
    assert buscada.status == StatusVenda.CONCLUIDO
    assert buscada.data_cancelamento is None
    assert buscada.id_usuario_cancelamento is None
    assert len(buscada.itens) == 2
    itens = {item.id_produto: item for item in buscada.itens}
    for esperado in venda.itens:
        item = itens[esperado.id_produto]
        assert item.id_venda_item == esperado.id_venda_item
        assert item.id_venda == venda.id_venda
        assert item.nome_produto == esperado.nome_produto
        assert item.quantidade == esperado.quantidade
        assert item.preco_unitario == esperado.preco_unitario


def test_buscar_venda_inexistente(dados):
    assert dados["repository"].buscar_por_id(-1) is None


def test_buscar_venda_retorna_apenas_seus_itens(dados, venda):
    repository = dados["repository"]
    repository.criar(venda)
    outra_venda = Venda(
        id_cliente=dados["id_cliente"],
        id_usuario=dados["id_usuario"],
        itens=[
            VendaItem(
                id_produto=dados["mouse"].id_produto,
                nome_produto="TESTE_MOUSE",
                quantidade=1,
                preco_unitario=Decimal("25.00"),
            )
        ],
        preco_total=Decimal("25.00"),
        status=StatusVenda.CONCLUIDO,
    )
    repository.criar(outra_venda)

    buscada = repository.buscar_por_id(venda.id_venda)
    assert buscada is not None
    itens = buscada.itens

    assert sorted(item.id_venda_item for item in itens) == sorted(
        item.id_venda_item for item in venda.itens
    )
    assert all(item.id_venda == venda.id_venda for item in itens)


def test_listar_resumo_filtra_status(dados, venda):
    repository = dados["repository"]
    repository.criar(venda)

    resumos = repository.listar_resumo(StatusVenda.CONCLUIDO)
    resumo = next(item for item in resumos if item.id_venda == venda.id_venda)

    assert isinstance(resumo, VendaResumo)
    assert resumo.nome_cliente == "TESTE_CLIENTE_VENDA"
    assert resumo.nome_vendedor == "TESTE_USUARIO_VENDA"
    assert resumo.data_venda == venda.data_hora
    assert resumo.valor_total == Decimal("150.00")
    assert all(item.status == StatusVenda.CONCLUIDO for item in resumos)

    repository.cancelar_venda(
        venda.id_venda, datetime.now(timezone.utc), dados["id_usuario"]
    )

    concluidas = repository.listar_resumo(StatusVenda.CONCLUIDO)
    canceladas = repository.listar_resumo(StatusVenda.CANCELADO)

    assert venda.id_venda not in [item.id_venda for item in concluidas]
    assert venda.id_venda in [item.id_venda for item in canceladas]
    assert all(item.status == StatusVenda.CANCELADO for item in canceladas)


@pytest.mark.parametrize('explicito', [False, True])
def test_listar_resumo_sem_filtro_inclui_todos_os_status(dados, venda, explicito):
    repository = dados['repository']
    outra_venda = deepcopy(venda)
    repository.criar(venda)
    repository.criar(outra_venda)
    repository.cancelar_venda(
        outra_venda.id_venda, datetime.now(timezone.utc), dados['id_usuario']
    )

    resumos = repository.listar_resumo(None) if explicito else repository.listar_resumo()
    status_por_id = {item.id_venda: item.status for item in resumos}

    assert status_por_id[venda.id_venda] == StatusVenda.CONCLUIDO
    assert status_por_id[outra_venda.id_venda] == StatusVenda.CANCELADO


def test_cancelar_venda_preserva_dados_e_itens(dados, venda):
    repository = dados["repository"]
    repository.criar(venda)
    data_cancelamento = datetime.now(timezone.utc)

    repository.cancelar_venda(
        venda.id_venda, data_cancelamento, dados["id_usuario"]
    )
    cancelada = repository.buscar_por_id(venda.id_venda)

    assert cancelada.status == StatusVenda.CANCELADO
    assert cancelada.data_cancelamento == data_cancelamento
    assert cancelada.id_usuario_cancelamento == dados["id_usuario"]
    assert cancelada.id_cliente == venda.id_cliente
    assert cancelada.id_usuario == venda.id_usuario
    assert cancelada.data_hora == venda.data_hora
    assert cancelada.preco_total == venda.preco_total
    assert sorted(item.id_venda_item for item in cancelada.itens) == sorted(
        item.id_venda_item for item in venda.itens
    )


def test_cancelar_venda_inexistente(dados):
    with pytest.raises(ValueError, match="nao encontrada"):
        dados["repository"].cancelar_venda(
            -1, datetime.now(timezone.utc), dados["id_usuario"]
        )


def test_cancelar_venda_ja_cancelada(dados, venda):
    repository = dados["repository"]
    repository.criar(venda)
    data_cancelamento = datetime(2026, 1, 1, tzinfo=timezone.utc)
    repository.cancelar_venda(
        venda.id_venda, data_cancelamento, dados["id_usuario"]
    )

    with pytest.raises(ValueError, match="ja esta Cancelada"):
        repository.cancelar_venda(
            venda.id_venda, datetime.now(timezone.utc), dados["id_usuario"]
        )

    buscada = repository.buscar_por_id(venda.id_venda)
    assert buscada.data_cancelamento == data_cancelamento


def test_criar_venda_e_itens_permite_rollback(dados, venda):
    repository = dados["repository"]
    repository.criar(venda)

    dados["conn"].rollback()

    assert repository.buscar_por_id(venda.id_venda) is None
    with dados["conn"].cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM venda_itens WHERE id_venda = %s",
            (venda.id_venda,),
        )
        assert cursor.fetchone()[0] == 0
