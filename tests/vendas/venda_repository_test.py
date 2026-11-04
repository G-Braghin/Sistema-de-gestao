from datetime import timedelta
from decimal import Decimal

from src.entities.dtos.produtos_vendidos_resumo import ProdutosVendidosResumo
from src.entities.dtos.venda_resumo import VendaResumo
from src.enums import StatusVenda
from src.models import Venda
from tests.vendas.conftest import VendaFactory, VendaItensFactory


def test_criar_venda_e_buscar_por_id(
    venda_repository, usuario_db, cliente_db, produto_db, mock_db_time
):
    venda = VendaFactory(
        id_usuario=usuario_db.id,
        id_cliente=cliente_db.id,
        itens=[VendaItensFactory(id_produto=produto_db.id)],
    )

    with mock_db_time(model=Venda) as hora:
        criada = venda_repository.criar(venda)

    resultado = venda_repository.buscar_por_id(criada.id)

    assert criada.id is not None
    assert criada.created_at == hora
    assert criada.itens[0].id is not None
    assert criada.itens[0].id_venda == criada.id
    assert resultado is not None
    assert resultado.id == criada.id
    assert resultado.id_cliente == cliente_db.id
    assert resultado.id_usuario == usuario_db.id
    assert resultado.itens[0].id == criada.itens[0].id


def test_buscar_venda_inexistente_retorna_none(venda_repository):
    assert venda_repository.buscar_por_id(9999999) is None


def test_cancelar_venda_e_listar_resumo_por_status(
    venda_repository, venda, cliente_db, usuario_db
):
    outra_venda = VendaFactory(
        id_usuario=usuario_db.id,
        id_cliente=cliente_db.id,
        itens=[VendaItensFactory(id_produto=venda.itens[0].id_produto)],
    )
    venda_repository.criar(outra_venda)

    cancelada = venda_repository.cancelar_venda(outra_venda.id)

    assert cancelada is not None
    assert cancelada.status == StatusVenda.CANCELADA
    assert venda_repository.cancelar_venda(outra_venda.id) is None
    assert venda_repository.cancelar_venda(9999999) is None

    data_inicio = venda.created_at.date()
    data_fim = data_inicio + timedelta(days=1)
    concluidas = venda_repository.listar_resumo(
        data_inicio, data_fim, StatusVenda.CONCLUIDA
    )
    canceladas = venda_repository.listar_resumo(
        data_inicio, data_fim, StatusVenda.CANCELADA
    )
    todas = venda_repository.listar_resumo(data_inicio, data_fim)

    assert len(concluidas) == len(canceladas) == 1
    assert isinstance(concluidas[0], VendaResumo)
    assert concluidas[0].id_venda == venda.id
    assert concluidas[0].nome_cliente == cliente_db.nome
    assert concluidas[0].nome_vendedor == usuario_db.nome
    assert concluidas[0].data_venda == venda.created_at
    assert concluidas[0].valor_total == venda.valor_total
    assert canceladas[0].id_venda == outra_venda.id
    assert {resumo.status for resumo in todas} == {
        StatusVenda.CONCLUIDA,
        StatusVenda.CANCELADA,
    }


def test_listar_produtos_mais_vendidos_agrupa_quantidade_e_valor(
    venda_repository, venda, produto_db
):
    outra_venda = VendaFactory(
        id_usuario=venda.id_usuario,
        id_cliente=venda.id_cliente,
        itens=[
            VendaItensFactory(
                id_produto=venda.itens[0].id_produto,
                quantidade=2,
                preco_unitario=Decimal('10.00'),
            )
        ],
    )
    venda_repository.criar(outra_venda)

    data_inicio = venda.created_at.date()
    resultado = venda_repository.listar_produtos_mais_vendidos(
        data_inicio, data_inicio + timedelta(days=1)
    )

    assert resultado == [
        ProdutosVendidosResumo(
            id_produto=venda.itens[0].id_produto,
            nome_produto=produto_db.nome,
            quantidade_vendida=5,
            valor_total=Decimal('50.00'),
        )
    ]
