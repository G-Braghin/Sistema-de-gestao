from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.entities.dtos.produtos_vendidos_resumo import ProdutosVendidosResumo
from src.enums import MotivoMovimentacao, StatusVenda
from src.utils.filtro_datas import FiltroDatas
from src.utils.fuso import FUSO_HORARIO
from tests.produtos.conftest import ProductFactory


def test_realizar_venda_com_dados_validos(
    venda_service,
    client_repository_mock,
    product_repository_mock,
    mock_venda_repo,
    mock_estoque_service,
    cliente,
    user_funcionario,
    produto,
):
    produto2 = ProductFactory(
        preco=Decimal('15.00'),
    )
    produto.id = 1
    produto2.id = 2
    produto.preco = Decimal('10.00')

    client_repository_mock.buscar_por_id.return_value = cliente

    product_repository_mock.buscar_por_id_para_atualizar.side_effect = [
        produto,
        produto2,
    ]

    mock_venda_repo.criar.side_effect = lambda venda: setattr(venda, 'id', 1) or venda

    itens = [
        {'id_produto': produto.id, 'quantidade': 2},
        {'id_produto': produto2.id, 'quantidade': 3},
    ]

    resultado = venda_service.realizar_venda(
        usuario_logado=user_funcionario,
        id_cliente=cliente.id,
        itens=itens,
    )

    assert resultado.id == 1
    assert resultado.id_cliente == cliente.id
    assert resultado.id_usuario == user_funcionario.id
    assert resultado.status == StatusVenda.CONCLUIDA

    assert resultado.valor_total == Decimal('65.00')

    # assert len(resultado.itens) == 2

    mock_venda_repo.criar.assert_called_once()

    assert mock_estoque_service.dar_saida.call_count == 2


@pytest.mark.parametrize(
    'caso',
    [
        (99999999, None, 'Cliente nao encontrado.'),
        (99, False, 'Cliente nao pode estar desativado.'),
    ],
)
def test_realizar_venda_com_cliente_invalido(
    venda_service, client_repository_mock, caso, cliente, user_funcionario
):
    id_cliente, ativo, mensagem = caso

    if ativo is None:
        client_repository_mock.buscar_por_id.return_value = None
    else:
        cliente.ativo = ativo
        client_repository_mock.buscar_por_id.return_value = cliente

    with pytest.raises(ValueError, match=mensagem):
        venda_service.realizar_venda(user_funcionario, id_cliente, [])

    client_repository_mock.buscar_por_id.assert_called_once()


def test_realizar_venda_sem_itens(venda_service, user_funcionario):
    with pytest.raises(ValueError, match='Ao menos deve ter um item'):
        venda_service.realizar_venda(user_funcionario, 1, [])


@pytest.mark.parametrize(
    ('item', 'mensagem'),
    [
        ({'quantidade': 1}, 'ID obrigatorio'),
        ({'id_produto': 1}, 'deve ter uma quantidade'),
    ],
)
def test_criar_item_venda_sem_campo_obrigatorio(venda_service, item, mensagem):
    with pytest.raises(ValueError, match=mensagem):
        venda_service._criar_item_venda(item)


@pytest.mark.parametrize(
    'caso',
    [
        ({'id_produto': 1, 'quantidade': 0}, ValueError),
        ({'id_produto': 1, 'quantidade': True}, TypeError),
        ({'id_produto': 0, 'quantidade': 1}, ValueError),
    ],
)
def test_criar_item_venda_com_dados_invalidos(
    venda_service, product_repository_mock, caso
):
    item, erro = caso
    with pytest.raises(erro):
        venda_service._criar_item_venda(item)

    product_repository_mock.buscar_por_id_para_atualizar.assert_not_called()


def test_criar_item_venda_com_produto_inexistente(
    venda_service, product_repository_mock, mock_estoque_service
):
    product_repository_mock.buscar_por_id_para_atualizar.return_value = None

    with pytest.raises(ValueError, match='nao encontrado'):
        venda_service._criar_item_venda({'id_produto': 1, 'quantidade': 1})

    mock_estoque_service.validar_disponibilidade.assert_not_called()


def test_criar_item_venda_com_estoque_insuficiente(
    venda_service, product_repository_mock, mock_estoque_service
):
    produto = Mock(nome='Teclado', quantidade_estoque=0)
    product_repository_mock.buscar_por_id_para_atualizar.return_value = produto
    mock_estoque_service.validar_disponibilidade.return_value = False

    with pytest.raises(ValueError, match='Estoque insuficiente'):
        venda_service._criar_item_venda({'id_produto': 1, 'quantidade': 1})


def test_cancelar_venda_com_dados_validos(
    venda_service, mock_venda_repo, mock_estoque_service, user_gerente, venda_fake
):
    mock_venda_repo.buscar_por_id.return_value = venda_fake

    resultado = venda_service.cancelar_venda(
        usuario_logado=user_gerente,
        id_venda=venda_fake.id,
    )

    mock_venda_repo.cancelar_venda.assert_called_once_with(
        id_venda=venda_fake.id,
    )

    assert resultado == venda_fake

    assert mock_estoque_service.dar_entrada.call_count == len(venda_fake.itens)

    for item in venda_fake.itens:
        mock_estoque_service.dar_entrada.assert_any_call(
            usuario_logado=user_gerente,
            id_produto=item.id_produto,
            entrada_estoque=item.quantidade,
            motivo=MotivoMovimentacao.CANCELAMENTO_VENDA,
            id_venda=item.id_venda,
        )


def test_cancelar_venda_sem_permissao(venda_service, mock_venda_repo, user_funcionario):
    with pytest.raises(PermissionError, match='Sem permissao'):
        venda_service.cancelar_venda(user_funcionario, 1)

    mock_venda_repo.cancelar_venda.assert_not_called()


def test_listar_resumo_retorna_vendas(venda_service, mock_venda_repo, user_gerente):
    vendas = [object()]
    mock_venda_repo.listar_resumo.return_value = vendas
    inicio = date(2026, 9, 1)
    final = date(2026, 9, 30)

    resultado = venda_service.listar_resumo(
        user_gerente,
        filtro_data=FiltroDatas.PERSONALIZADO,
        inicio_filtro=inicio,
        final_filtro=final,
    )

    assert resultado == vendas
    mock_venda_repo.listar_resumo.assert_called_once_with(
        datetime(2026, 9, 1, 3, tzinfo=timezone.utc),
        datetime(2026, 10, 1, 3, tzinfo=timezone.utc),
        None,
    )


def test_listar_resumo_sem_permissao(venda_service, mock_venda_repo, user_funcionario):
    with pytest.raises(PermissionError, match='Sem permissao'):
        venda_service.listar_resumo(user_funcionario)

    mock_venda_repo.listar_resumo.assert_not_called()


def test_listar_resumo_usa_filtro_mes_atual_por_padrao(
    venda_service, mock_venda_repo, user_gerente
):
    venda_service.listar_resumo(user_gerente)

    mock_venda_repo.listar_resumo.assert_called_once()


def test_listar_resumo_com_datas_invalidas(
    venda_service, mock_venda_repo, user_gerente
):
    with pytest.raises(ValueError, match='As duas datas devem estar preenchidas'):
        venda_service.listar_resumo(
            user_gerente,
            filtro_data=FiltroDatas.PERSONALIZADO,
            inicio_filtro=date(2026, 9, 1),
        )

    mock_venda_repo.listar_resumo.assert_not_called()


@pytest.mark.parametrize(
    ('filtro', 'inicio', 'final'),
    [
        (FiltroDatas.HOJE, date(2025, 12, 31), date(2026, 1, 1)),
        (FiltroDatas.ONTEM, date(2025, 12, 30), date(2025, 12, 31)),
        (FiltroDatas.ULTIMOS_7_DIAS, date(2025, 12, 25), date(2026, 1, 1)),
        (FiltroDatas.ULTIMOS_30_DIAS, date(2025, 12, 2), date(2026, 1, 1)),
        (FiltroDatas.MES_ATUAL, date(2025, 12, 1), date(2026, 1, 1)),
        (FiltroDatas.MES_ANTERIOR, date(2025, 11, 1), date(2025, 12, 1)),
        (FiltroDatas.ANO_ATUAL, date(2025, 1, 1), date(2026, 1, 1)),
        (FiltroDatas.ANO_ANTERIOR, date(2024, 1, 1), date(2025, 1, 1)),
    ],
)
def test_obter_datas_filtro(venda_service, filtro, inicio, final):
    agora_utc = datetime(2026, 1, 1, 2, 30, tzinfo=timezone.utc)
    with patch('src.services.venda_service.datetime', wraps=datetime) as relogio:
        relogio.now.side_effect = agora_utc.astimezone
        resultado = venda_service._obter_datas_filtro(filtro)

    assert resultado == (inicio, final)
    relogio.now.assert_called_once_with(FUSO_HORARIO)


def test_listar_venda_itens_retorna_venda(
    venda_service, mock_venda_repo, user_gerente, venda_fake
):
    mock_venda_repo.buscar_por_id.return_value = venda_fake

    resultado = venda_service.listar_venda_itens(user_gerente, venda_fake.id)

    assert resultado is venda_fake
    mock_venda_repo.buscar_por_id.assert_called_once_with(venda_fake.id)


def test_listar_venda_itens_nao_encontrada(
    venda_service, mock_venda_repo, user_gerente
):
    mock_venda_repo.buscar_por_id.return_value = None

    with pytest.raises(ValueError, match='ID nao encontrado'):
        venda_service.listar_venda_itens(user_gerente, 1)


def test_listar_venda_itens_sem_permissao(
    venda_service, mock_venda_repo, user_funcionario
):
    with pytest.raises(PermissionError, match='Sem Permissao'):
        venda_service.listar_venda_itens(user_funcionario, 1)

    mock_venda_repo.buscar_por_id.assert_not_called()


def test_criar_resumo_relatorio_com_vendas_concluidas(
    venda_service,
    mock_venda_repo,
    user_gerente,
):
    vendas = [
        SimpleNamespace(valor_total=Decimal('50.00')),
        SimpleNamespace(valor_total=Decimal('100.00')),
        SimpleNamespace(valor_total=Decimal('150.00')),
    ]

    mock_venda_repo.listar_resumo.return_value = vendas

    data_inicial = date(2026, 11, 1)
    data_final = date(2026, 11, 5)

    resultado = venda_service.criar_resumo_relatorio(
        usuario_logado=user_gerente,
        data_inicial=data_inicial,
        data_final=data_final,
    )

    assert resultado is not None
    assert resultado.data_inicial == data_inicial
    assert resultado.data_final == data_final
    assert resultado.vendas_concluidas == 3
    assert resultado.total_periodo == Decimal('300.00')
    assert resultado.ticket_medio == Decimal('100.00')

    inicio, final = venda_service._obter_intervalo_filtro_datas(
        FiltroDatas.PERSONALIZADO,
        data_inicial,
        data_final,
    )

    mock_venda_repo.listar_resumo.assert_called_once_with(
        inicio,
        final,
        StatusVenda.CONCLUIDA,
    )


def test_criar_resumo_relatorio_sem_permissao(
    venda_service, mock_venda_repo, user_funcionario
):

    with pytest.raises(PermissionError, match='Sem permissao'):
        venda_service.criar_resumo_relatorio(
            user_funcionario, date(2026, 9, 1), date(2026, 9, 30)
        )

    mock_venda_repo.listar_resumo.assert_not_called()


def test_relatorio_produtos_com_dados_validos(
    venda_service,
    mock_venda_repo,
    user_gerente,
):
    relatorio_esperado = [MagicMock(spec=ProdutosVendidosResumo)]
    mock_venda_repo.listar_produtos_mais_vendidos.return_value = relatorio_esperado

    resultado = venda_service.relatorio_produtos(
        usuario_logado=user_gerente,
        data_inicial=date(2026, 11, 1),
        data_final=date(2026, 11, 5),
    )

    assert resultado == relatorio_esperado
    mock_venda_repo.listar_produtos_mais_vendidos.assert_called_once()


def test_relatorio_produtos_sem_permissao(
    venda_service, mock_venda_repo, user_funcionario
):
    with pytest.raises(PermissionError, match='Sem permissao'):
        venda_service.relatorio_produtos(
            user_funcionario, date(2026, 9, 1), date(2026, 9, 30)
        )

    mock_venda_repo.listar_produtos_mais_vendidos.assert_not_called()
