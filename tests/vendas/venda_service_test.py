from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, Mock, call, patch

import pytest
from src.entities.enums.papel_usuario import PapelUsuario
from src.entities.enums.status_venda import StatusVenda
from src.entities.produto import Produto
from src.entities.usuario import Usuario
from src.services.venda_service import VendaService
from src.utils.filtro_datas import FiltroDatas
from src.utils.fuso import FUSO_HORARIO
from src.entities.dtos.produtos_vendidos_resumo import ProdutosVendidosResumo


@pytest.fixture
def dados():
    conexao = Mock()
    conn = MagicMock()
    conn.__exit__.return_value = False
    conexao.get_connection.return_value = conn

    venda_repository = Mock()
    produto_repository = Mock()
    cliente_repository = Mock()
    estoque_service = Mock()

    cliente_repository.buscar_por_id.return_value = Mock(ativo=True)

    produtos = {
        1: Produto(
            id_produto=1,
            nome="TECLADO",
            marca="LOGITECH",
            preco=Decimal("100.00"),
            quantidade_estoque=10,
        ),
        2: Produto(
            id_produto=2,
            nome="MOUSE",
            marca="LOGITECH",
            preco=Decimal("25.00"),
            quantidade_estoque=10,
        ),
    }

    produto_repository.buscar_por_id.side_effect = produtos.get
    produto_repository.buscar_por_id_para_atualizar.side_effect = produtos.get
    estoque_service.validar_disponibilidade.return_value = True

    def criar(venda):
        venda.id_venda = 10
        for numero, item in enumerate(venda.itens, start=1):
            item.id_venda = venda.id_venda
            item.id_venda_item = numero
        return venda

    venda_repository.criar.side_effect = criar

    service = VendaService(
        conexao=conexao,
        venda_repository=venda_repository,
        produto_repository=produto_repository,
        cliente_repository=cliente_repository,
        estoque_service=estoque_service,
    )

    return {
        "service": service,
        "conn": conn,
        "venda_repository": venda_repository,
        "produto_repository": produto_repository,
        "cliente_repository": cliente_repository,
        "estoque_service": estoque_service,
    }


@pytest.fixture
def usuario():
    return Usuario(
        id_usuario=1,
        nome="TESTE_ADMIN",
        senha_hash="teste_hash",
        papel=PapelUsuario.ADMINISTRADOR,
    )


@pytest.mark.parametrize('papel', [PapelUsuario.ADMINISTRADOR, PapelUsuario.GERENTE])
def test_relatorio_produtos_retorna_dtos_e_ajusta_periodo(dados, usuario, papel):
    usuario.papel = papel
    produtos = [
        ProdutosVendidosResumo(2, 'MOUSE', 4, Decimal('100.00')),
        ProdutosVendidosResumo(1, 'TECLADO', 1, Decimal('150.00')),
    ]
    dados['venda_repository'].listar_produtos_mais_vendidos.return_value = produtos

    resultado = dados['service'].relatorio_produtos(
        usuario, date(2026, 9, 1), date(2026, 9, 30)
    )

    assert resultado == produtos
    dados['venda_repository'].listar_produtos_mais_vendidos.assert_called_once_with(
        datetime(2026, 9, 1, 3, tzinfo=timezone.utc), datetime(2026, 10, 1, 3, tzinfo=timezone.utc)
    )
    dados['conn'].__exit__.assert_called_once_with(None, None, None)


def test_relatorio_produtos_permite_consulta_de_um_dia(dados, usuario):
    dados['venda_repository'].listar_produtos_mais_vendidos.return_value = []

    dados['service'].relatorio_produtos(usuario, date(2025, 12, 31), date(2025, 12, 31))

    dados['venda_repository'].listar_produtos_mais_vendidos.assert_called_once_with(
        datetime(2025, 12, 31, 3, tzinfo=timezone.utc), datetime(2026, 1, 1, 3, tzinfo=timezone.utc)
    )


def test_relatorio_produtos_sem_resultados(dados, usuario):
    dados['venda_repository'].listar_produtos_mais_vendidos.return_value = []

    resultado = dados['service'].relatorio_produtos(
        usuario, date(2026, 9, 1), date(2026, 9, 30)
    )

    assert resultado == []


def test_relatorio_produtos_sem_permissao(dados, usuario):
    usuario.papel = PapelUsuario.FUNCIONARIO

    with pytest.raises(PermissionError, match='Sem permissao'):
        dados['service'].relatorio_produtos(usuario, date(2026, 9, 1), date(2026, 9, 30))

    dados['venda_repository'].listar_produtos_mais_vendidos.assert_not_called()
    dados['conn'].__enter__.assert_not_called()


@pytest.mark.parametrize('inicio, final, mensagem', [
    (date(2026, 9, 30), date(2026, 9, 1), 'data final nao pode ser anterior'),
    (None, date(2026, 9, 30), 'As duas datas devem estar preenchidas'),
    (date(2026, 9, 1), None, 'As duas datas devem estar preenchidas'),
])
def test_relatorio_produtos_com_datas_invalidas(dados, usuario, inicio, final, mensagem):
    with pytest.raises(ValueError, match=mensagem):
        dados['service'].relatorio_produtos(usuario, inicio, final)

    dados['venda_repository'].listar_produtos_mais_vendidos.assert_not_called()


def test_relatorio_produtos_propaga_erro_da_consulta(dados, usuario):
    erro = RuntimeError('Erro ao consultar produtos vendidos')
    dados['venda_repository'].listar_produtos_mais_vendidos.side_effect = erro

    with pytest.raises(RuntimeError, match='Erro ao consultar produtos vendidos'):
        dados['service'].relatorio_produtos(usuario, date(2026, 9, 1), date(2026, 9, 30))

    dados['conn'].__exit__.assert_called_once()
    assert dados['conn'].__exit__.call_args.args[0] is RuntimeError
    assert dados['conn'].__exit__.call_args.args[1] is erro


@pytest.mark.parametrize('filtro, inicio, final', [
    (FiltroDatas.HOJE, (2025, 12, 31), (2026, 1, 1)),
    (FiltroDatas.ONTEM, (2025, 12, 30), (2025, 12, 31)),
    (FiltroDatas.ULTIMOS_7_DIAS, (2025, 12, 25), (2026, 1, 1)),
    (FiltroDatas.ULTIMOS_30_DIAS, (2025, 12, 2), (2026, 1, 1)),
    (FiltroDatas.MES_ATUAL, (2025, 12, 1), (2026, 1, 1)),
    (FiltroDatas.MES_ANTERIOR, (2025, 11, 1), (2025, 12, 1)),
    (FiltroDatas.ANO_ATUAL, (2025, 1, 1), (2026, 1, 1)),
    (FiltroDatas.ANO_ANTERIOR, (2024, 1, 1), (2025, 1, 1)),
])
def test_filtros_usam_dia_de_brasilia_mesmo_quando_utc_ja_virou(
    dados, filtro, inicio, final
):
    agora_utc = datetime(2026, 1, 1, 2, 30, tzinfo=timezone.utc)
    with patch('src.services.venda_service.datetime', wraps=datetime) as relogio:
        relogio.now.side_effect = lambda fuso: agora_utc.astimezone(fuso)
        resultado = dados['service']._obter_intervalo_filtro_datas(filtro)

    assert resultado == (
        datetime(*inicio, 3, tzinfo=timezone.utc),
        datetime(*final, 3, tzinfo=timezone.utc),
    )
    relogio.now.assert_called_once_with(FUSO_HORARIO)


def test_filtro_personalizado_inclui_dia_inteiro_em_brasilia(dados):
    inicio, final = dados['service']._obter_intervalo_filtro_datas(
        FiltroDatas.PERSONALIZADO, date(2026, 10, 5), date(2026, 10, 5)
    )

    assert inicio == datetime(2026, 10, 5, 3, tzinfo=timezone.utc)
    assert final == datetime(2026, 10, 6, 3, tzinfo=timezone.utc)
    assert inicio <= datetime(2026, 10, 6, 2, 30, tzinfo=timezone.utc) < final
    assert not inicio <= datetime(2026, 10, 5, 2, 59, tzinfo=timezone.utc) < final


@pytest.fixture
def itens():
    return [
        {"id_produto": 1, "quantidade": 1},
        {"id_produto": 2, "quantidade": 2},
    ]


def test_realizar_venda_com_dados_validos(dados, usuario, itens):
    venda = dados["service"].realizar_venda(usuario, 1, itens)

    assert venda.id_venda == 10
    assert venda.id_cliente == 1
    assert venda.id_usuario == usuario.id_usuario
    assert venda.status == StatusVenda.CONCLUIDO
    assert venda.preco_total == Decimal("150.00")
    assert len(venda.itens) == 2

    assert venda.itens[0].nome_produto == "TECLADO"
    assert venda.itens[0].quantidade == 1
    assert venda.itens[0].preco_unitario == Decimal("100.00")

    assert venda.itens[1].nome_produto == "MOUSE"
    assert venda.itens[1].quantidade == 2
    assert venda.itens[1].preco_unitario == Decimal("25.00")

    dados["venda_repository"].criar.assert_called_once_with(venda)
    assert dados["estoque_service"].registrar_saida.call_args_list == [
        call(
            usuario_logado=usuario,
            id_produto=1,
            saida_estoque=1,
            id_venda=10,
        ),
        call(
            usuario_logado=usuario,
            id_produto=2,
            saida_estoque=2,
            id_venda=10,
        ),
    ]
    dados["conn"].__exit__.assert_called_once_with(None, None, None)


def test_realizar_venda_bloqueia_produtos_em_ordem_antes_de_salvar(dados, usuario, itens):
    operacoes = Mock()
    operacoes.attach_mock(dados['produto_repository'].buscar_por_id_para_atualizar, 'bloquear')
    operacoes.attach_mock(dados['venda_repository'].criar, 'criar')

    venda = dados['service'].realizar_venda(usuario, 1, list(reversed(itens)))

    assert operacoes.mock_calls == [call.bloquear(1), call.bloquear(2), call.criar(venda)]


def test_cancelar_venda_devolve_em_ordem_de_produto(dados, usuario, venda_salva):
    venda_salva.itens.reverse()

    dados['service'].cancelar_venda(usuario, venda_salva.id_venda)

    chamadas = dados['estoque_service'].registrar_entrada.call_args_list
    assert [chamada.kwargs['id_produto'] for chamada in chamadas] == [1, 2]


def test_realizar_venda_com_cliente_inexistente(dados, usuario, itens):
    dados["cliente_repository"].buscar_por_id.return_value = None

    with pytest.raises(ValueError, match="Cliente nao encontrado"):
        dados["service"].realizar_venda(usuario, 1, itens)

    dados["venda_repository"].criar.assert_not_called()
    dados["estoque_service"].registrar_saida.assert_not_called()


def test_realizar_venda_com_cliente_inativo(dados, usuario, itens):
    dados["cliente_repository"].buscar_por_id.return_value.ativo = False

    with pytest.raises(ValueError, match="Cliente nao pode estar desativado"):
        dados["service"].realizar_venda(usuario, 1, itens)

    dados["venda_repository"].criar.assert_not_called()
    dados["estoque_service"].registrar_saida.assert_not_called()


def test_realizar_venda_sem_itens(dados, usuario):
    with pytest.raises(ValueError, match="Ao menos deve ter um item"):
        dados["service"].realizar_venda(usuario, 1, [])

    dados["venda_repository"].criar.assert_not_called()
    dados["estoque_service"].registrar_saida.assert_not_called()


def test_realizar_venda_com_quantidade_booleana(dados, usuario):
    itens = [{"id_produto": 1, "quantidade": True}]

    with pytest.raises(TypeError, match="Quantidade deve ser um numero inteiro"):
        dados["service"].realizar_venda(usuario, 1, itens)

    dados["produto_repository"].buscar_por_id.assert_not_called()
    dados["venda_repository"].criar.assert_not_called()


def test_realizar_venda_com_quantidade_zero(dados, usuario):
    itens = [{"id_produto": 1, "quantidade": 0}]

    with pytest.raises(ValueError, match="maior que 0"):
        dados["service"].realizar_venda(usuario, 1, itens)

    dados["venda_repository"].criar.assert_not_called()
    dados["estoque_service"].registrar_saida.assert_not_called()


def test_realizar_venda_com_id_produto_invalido(dados, usuario):
    itens = [{"id_produto": 0, "quantidade": 1}]

    with pytest.raises(ValueError):
        dados["service"].realizar_venda(usuario, 1, itens)

    dados["produto_repository"].buscar_por_id.assert_not_called()
    dados["venda_repository"].criar.assert_not_called()


def test_realizar_venda_com_produto_inexistente(dados, usuario):
    itens = [{"id_produto": 999, "quantidade": 1}]

    with pytest.raises(ValueError, match="nao encontrado"):
        dados["service"].realizar_venda(usuario, 1, itens)

    dados["venda_repository"].criar.assert_not_called()
    dados["estoque_service"].registrar_saida.assert_not_called()


def test_realizar_venda_com_estoque_insuficiente(dados, usuario, itens):
    dados["estoque_service"].validar_disponibilidade.return_value = False

    with pytest.raises(ValueError, match="Estoque insuficiente"):
        dados["service"].realizar_venda(usuario, 1, itens)

    dados["venda_repository"].criar.assert_not_called()
    dados["estoque_service"].registrar_saida.assert_not_called()


def test_realizar_venda_propaga_falha_na_segunda_saida(dados, usuario, itens):
    erro = RuntimeError("Erro ao registrar saida")
    dados["estoque_service"].registrar_saida.side_effect = [None, erro]

    with pytest.raises(RuntimeError, match="Erro ao registrar saida"):
        dados["service"].realizar_venda(usuario, 1, itens)

    dados["venda_repository"].criar.assert_called_once()
    assert dados["estoque_service"].registrar_saida.call_count == 2

    dados["conn"].__exit__.assert_called_once()
    assert dados["conn"].__exit__.call_args.args[0] is RuntimeError
    assert dados["conn"].__exit__.call_args.args[1] is erro


@pytest.fixture
def venda_salva(dados, usuario, itens):
    venda = dados["service"].realizar_venda(usuario, 1, itens)

    dados["conn"].reset_mock()
    dados["venda_repository"].reset_mock()
    dados["estoque_service"].reset_mock()

    dados["venda_repository"].buscar_por_id.return_value = venda
    return venda


def test_cancelar_venda_devolve_todos_os_itens(dados, usuario, venda_salva):
    inicio = datetime.now(timezone.utc)

    dados["service"].cancelar_venda(usuario, venda_salva.id_venda)

    fim = datetime.now(timezone.utc)
    repository = dados["venda_repository"]
    repository.cancelar_venda.assert_called_once()

    argumentos = repository.cancelar_venda.call_args.kwargs
    assert argumentos["id_venda"] == venda_salva.id_venda
    assert argumentos["id_usuario_cancelamento"] == usuario.id_usuario
    assert inicio <= argumentos["data_cancelamento"] <= fim

    assert dados["estoque_service"].registrar_entrada.call_args_list == [
        call(
            usuario_logado=usuario,
            id_produto=1,
            entrada_estoque=1,
            id_venda=venda_salva.id_venda,
        ),
        call(
            usuario_logado=usuario,
            id_produto=2,
            entrada_estoque=2,
            id_venda=venda_salva.id_venda,
        ),
    ]
    dados["conn"].__exit__.assert_called_once_with(None, None, None)


def test_cancelar_venda_sem_permissao(dados, usuario):
    usuario.papel = PapelUsuario.FUNCIONARIO

    with pytest.raises(PermissionError, match="Sem permissao"):
        dados["service"].cancelar_venda(usuario, 10)

    dados["venda_repository"].cancelar_venda.assert_not_called()
    dados["estoque_service"].registrar_entrada.assert_not_called()


def test_cancelamento_recusado_nao_devolve_estoque(dados, usuario):
    dados["venda_repository"].cancelar_venda.side_effect = ValueError(
        "Venda nao encontrada ou ja esta Cancelada."
    )

    with pytest.raises(ValueError, match="ja esta Cancelada"):
        dados["service"].cancelar_venda(usuario, 10)

    dados["venda_repository"].buscar_por_id.assert_not_called()
    dados["estoque_service"].registrar_entrada.assert_not_called()


def test_cancelar_venda_propaga_falha_na_devolucao(dados, usuario, venda_salva):
    erro = RuntimeError("Erro ao devolver estoque")
    dados["estoque_service"].registrar_entrada.side_effect = [None, erro]

    with pytest.raises(RuntimeError, match="Erro ao devolver estoque"):
        dados["service"].cancelar_venda(usuario, venda_salva.id_venda)

    dados["venda_repository"].cancelar_venda.assert_called_once()
    assert dados["estoque_service"].registrar_entrada.call_count == 2

    dados["conn"].__exit__.assert_called_once()
    assert dados["conn"].__exit__.call_args.args[0] is RuntimeError
    assert dados["conn"].__exit__.call_args.args[1] is erro


def test_cancelar_venda_retorna_venda_cancelada(dados, usuario, venda_salva):
    data_cancelamento = datetime.now(timezone.utc)

    venda_salva.status = StatusVenda.CANCELADO
    venda_salva.data_cancelamento = data_cancelamento
    venda_salva.id_usuario_cancelamento = usuario.id_usuario

    dados["venda_repository"].buscar_por_id.return_value = venda_salva

    resultado = dados["service"].cancelar_venda(usuario, venda_salva.id_venda)

    assert resultado is venda_salva
    assert resultado.status == StatusVenda.CANCELADO
    assert resultado.data_cancelamento == data_cancelamento
    assert resultado.id_usuario_cancelamento == usuario.id_usuario

    dados["venda_repository"].buscar_por_id.assert_called_once_with(
        venda_salva.id_venda
    )
    dados["conn"].__exit__.assert_called_once_with(None, None, None)


def test_listar_resumo_de_vendas_canceladas(dados, usuario):
    resumos = [Mock(status=StatusVenda.CANCELADO)]
    dados["venda_repository"].listar_resumo.return_value = resumos
    data_inicio, data_fim = dados["service"]._obter_intervalo_filtro_datas(
        FiltroDatas.MES_ATUAL
    )

    resultado = dados["service"].listar_resumo(usuario, StatusVenda.CANCELADO)

    assert resultado == resumos
    dados["venda_repository"].listar_resumo.assert_called_once_with(
        data_inicio, data_fim, StatusVenda.CANCELADO
    )


def test_listar_resumo_sem_vendas(dados, usuario):
    dados["venda_repository"].listar_resumo.return_value = []
    data_inicio, data_fim = dados["service"]._obter_intervalo_filtro_datas(
        FiltroDatas.MES_ATUAL
    )

    resultado = dados["service"].listar_resumo(usuario)

    assert resultado == []
    dados["venda_repository"].listar_resumo.assert_called_once_with(
        data_inicio, data_fim, None
    )


def test_listar_resumo_sem_permissao(dados, usuario):
    usuario.papel = PapelUsuario.FUNCIONARIO

    with pytest.raises(PermissionError, match="Sem permissao"):
        dados["service"].listar_resumo(usuario)

    dados["venda_repository"].listar_resumo.assert_not_called()


def test_consultar_venda_com_itens(dados, usuario, venda_salva):
    resultado = dados["service"].listar_venda_itens(usuario, venda_salva.id_venda)

    assert resultado is venda_salva
    assert len(resultado.itens) == 2
    dados["venda_repository"].buscar_por_id.assert_called_once_with(
        venda_salva.id_venda
    )


def test_consultar_venda_inexistente(dados, usuario):
    dados["venda_repository"].buscar_por_id.return_value = None

    with pytest.raises(ValueError, match="ID nao encontrado"):
        dados["service"].listar_venda_itens(usuario, 999)


def test_consultar_venda_sem_permissao(dados, usuario):
    usuario.papel = PapelUsuario.FUNCIONARIO

    with pytest.raises(PermissionError, match="Sem Permissao"):
        dados["service"].listar_venda_itens(usuario, 10)

    dados["venda_repository"].buscar_por_id.assert_not_called()


def test_criar_resumo_relatorio_calcula_total_quantidade_e_ticket(dados, usuario):
    dados["venda_repository"].listar_resumo.return_value = [
        Mock(valor_total=Decimal("20.10")),
        Mock(valor_total=Decimal("40.20")),
    ]
    data_inicial = date(2026, 9, 1)
    data_final = date(2026, 9, 30)

    relatorio = dados["service"].criar_resumo_relatorio(
        usuario, data_inicial, data_final
    )

    assert relatorio.data_inicial == data_inicial
    assert relatorio.data_final == data_final
    assert relatorio.vendas_concluidas == 2
    assert relatorio.total_periodo == Decimal("60.30")
    assert relatorio.ticket_medio == Decimal("30.15")
    assert isinstance(relatorio.total_periodo, Decimal)
    assert isinstance(relatorio.ticket_medio, Decimal)
    dados["venda_repository"].listar_resumo.assert_called_once_with(
        datetime(2026, 9, 1, 3, tzinfo=timezone.utc),
        datetime(2026, 10, 1, 3, tzinfo=timezone.utc), StatusVenda.CONCLUIDO
    )


def test_criar_resumo_relatorio_com_gerente_e_uma_venda_no_mesmo_dia(dados, usuario):
    usuario.papel = PapelUsuario.GERENTE
    dados["venda_repository"].listar_resumo.return_value = [
        Mock(valor_total=Decimal("19.90"))
    ]
    dia = date(2025, 12, 31)

    relatorio = dados["service"].criar_resumo_relatorio(usuario, dia, dia)

    assert relatorio.data_inicial == dia
    assert relatorio.data_final == dia
    assert relatorio.vendas_concluidas == 1
    assert relatorio.total_periodo == Decimal("19.90")
    assert relatorio.ticket_medio == Decimal("19.90")
    dados["venda_repository"].listar_resumo.assert_called_once_with(
        datetime(2025, 12, 31, 3, tzinfo=timezone.utc),
        datetime(2026, 1, 1, 3, tzinfo=timezone.utc), StatusVenda.CONCLUIDO
    )


def test_criar_resumo_relatorio_sem_vendas(dados, usuario):
    dados["venda_repository"].listar_resumo.return_value = []

    resultado = dados["service"].criar_resumo_relatorio(
        usuario, date(2026, 9, 1), date(2026, 9, 30)
    )

    assert resultado is None
    dados["venda_repository"].listar_resumo.assert_called_once_with(
        datetime(2026, 9, 1, 3, tzinfo=timezone.utc), datetime(2026, 10, 1, 3, tzinfo=timezone.utc), StatusVenda.CONCLUIDO
    )


def test_criar_resumo_relatorio_sem_permissao(dados, usuario):
    usuario.papel = PapelUsuario.FUNCIONARIO

    with pytest.raises(PermissionError, match="Sem permissao para ver relatorios"):
        dados["service"].criar_resumo_relatorio(
            usuario, date(2026, 9, 1), date(2026, 9, 30)
        )

    dados["venda_repository"].listar_resumo.assert_not_called()


def test_criar_resumo_relatorio_com_datas_invertidas(dados, usuario):
    with pytest.raises(ValueError, match="data final nao pode ser anterior"):
        dados["service"].criar_resumo_relatorio(
            usuario, date(2026, 9, 30), date(2026, 9, 1)
        )

    dados["venda_repository"].listar_resumo.assert_not_called()


def test_criar_resumo_relatorio_sem_data_inicial(dados, usuario):
    with pytest.raises(ValueError, match="As duas datas devem estar preenchidas"):
        dados["service"].criar_resumo_relatorio(usuario, None, date(2026, 9, 30))

    dados["venda_repository"].listar_resumo.assert_not_called()


def test_criar_resumo_relatorio_sem_data_final(dados, usuario):
    with pytest.raises(ValueError, match="As duas datas devem estar preenchidas"):
        dados["service"].criar_resumo_relatorio(usuario, date(2026, 9, 1), None)

    dados["venda_repository"].listar_resumo.assert_not_called()


def test_criar_resumo_relatorio_propaga_falha_na_consulta(dados, usuario):
    erro = RuntimeError("Erro ao consultar vendas")
    dados["venda_repository"].listar_resumo.side_effect = erro

    with pytest.raises(RuntimeError, match="Erro ao consultar vendas"):
        dados["service"].criar_resumo_relatorio(
            usuario, date(2026, 9, 1), date(2026, 9, 30)
        )

    dados["conn"].__exit__.assert_called_once()
    assert dados["conn"].__exit__.call_args.args[0] is RuntimeError
    assert dados["conn"].__exit__.call_args.args[1] is erro
