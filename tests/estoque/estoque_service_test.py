from decimal import Decimal

import pytest

from src.entities.dtos.relatorio_estoque_resumo import RelatorioEstoqueResumo
from src.enums import MotivoMovimentacao, PapelEnum, TipoMovimentacao
from src.models import Movimentacao, Produto


def criar_produto(nome, preco, quantidade, id_produto):
    produto = Produto(nome=nome, preco=preco, quantidade=quantidade)
    produto.id = id_produto
    return produto


@pytest.mark.parametrize('operacao', ['dar_entrada', 'dar_saida'])
def test_funcionario_nao_pode_alterar_estoque(
    estoque_service,
    mock_product_repository,
    mock_mov_repository,
    operacao,
    user_funcionario,
):

    with pytest.raises(PermissionError, match='Sem permissao'):
        getattr(estoque_service, operacao)(
            user_funcionario, 1, 5, MotivoMovimentacao.AJUSTE
        )

    mock_product_repository.buscar_por_id_para_atualizar.assert_not_called()
    mock_product_repository.atualizar.assert_not_called()
    mock_mov_repository.criar.assert_not_called()


def test_dar_entrada_com_quantidade_valida(
    estoque_service, mock_product_repository, mock_mov_repository, user_gerente, produto
):
    quantidade_antes = produto.quantidade

    mock_product_repository.buscar_por_id_para_atualizar.return_value = produto

    quantidade_entrada = 10

    resultado = estoque_service.dar_entrada(
        usuario_logado=user_gerente,
        id_produto=produto.id,
        entrada_estoque=quantidade_entrada,
        motivo=MotivoMovimentacao.REPOSICAO,
    )

    assert produto.quantidade == quantidade_entrada + quantidade_antes

    mock_product_repository.buscar_por_id_para_atualizar.assert_called_once_with(
        produto.id
    )
    mock_product_repository.atualizar.assert_called_once_with(produto)

    mock_mov_repository.criar.assert_called_once()

    movimentacao = mock_mov_repository.criar.call_args.args[0]

    assert resultado is movimentacao
    assert movimentacao.id_produto == produto.id
    assert movimentacao.id_usuario == user_gerente.id
    assert movimentacao.motivo == MotivoMovimentacao.REPOSICAO
    assert movimentacao.tipo_movimentacao == TipoMovimentacao.ENTRADA
    assert movimentacao.quantidade == quantidade_entrada


@pytest.mark.parametrize('operacao', ['dar_entrada', 'dar_saida'])
def test_alterar_estoque_produto_inexistente(
    estoque_service,
    mock_product_repository,
    mock_mov_repository,
    user_gerente,
    operacao,
):
    mock_product_repository.buscar_por_id_para_atualizar.return_value = None

    with pytest.raises(LookupError, match='Produto nao encontrado'):
        getattr(estoque_service, operacao)(
            user_gerente,
            999999,
            10,
            MotivoMovimentacao.REPOSICAO,
        )

    mock_product_repository.atualizar.assert_not_called()
    mock_mov_repository.criar.assert_not_called()


def test_dar_saida_com_quantidade_valida(
    estoque_service, mock_product_repository, mock_mov_repository, user_gerente, produto
):
    quantidade_inicial = 10
    quantidade_saida = 4
    produto.quantidade = quantidade_inicial
    mock_product_repository.buscar_por_id_para_atualizar.return_value = produto

    mock_mov_repository.criar.return_value = None

    resultado = estoque_service.dar_saida(
        usuario_logado=user_gerente,
        id_produto=produto.id,
        saida_estoque=quantidade_saida,
        motivo=MotivoMovimentacao.AJUSTE,
    )

    assert resultado is mock_mov_repository.criar.call_args.args[0]
    assert produto.quantidade == quantidade_inicial - quantidade_saida

    mock_product_repository.buscar_por_id_para_atualizar.assert_called_once_with(
        produto.id
    )
    mock_product_repository.atualizar.assert_called_once_with(produto)

    mock_mov_repository.criar.assert_called_once()

    movimentacao = mock_mov_repository.criar.call_args.args[0]

    assert isinstance(movimentacao, Movimentacao)
    assert movimentacao.id_produto == produto.id
    assert movimentacao.id_usuario == user_gerente.id
    assert movimentacao.motivo == MotivoMovimentacao.AJUSTE
    assert movimentacao.tipo_movimentacao == TipoMovimentacao.SAIDA
    assert movimentacao.quantidade == quantidade_saida


def test_dar_saida_com_estoque_insuficiente(
    estoque_service, mock_product_repository, mock_mov_repository, user_gerente, produto
):
    quantidade_inicial = 10
    quantidade_saida = 11
    produto.quantidade = quantidade_inicial
    mock_product_repository.buscar_por_id_para_atualizar.return_value = produto

    with pytest.raises(ValueError, match='Estoque indisponivel'):
        estoque_service.dar_saida(
            usuario_logado=user_gerente,
            id_produto=produto.id,
            saida_estoque=quantidade_saida,
            motivo=MotivoMovimentacao.AJUSTE,
        )

    assert produto.quantidade == quantidade_inicial

    mock_product_repository.atualizar.assert_not_called()
    mock_mov_repository.criar.assert_not_called()


def test_listar_movimentacoes_com_administrador(
    estoque_service, mock_mov_repository, user_gerente
):
    user_gerente.papel = PapelEnum.ADMIN

    movimentacoes = [
        Movimentacao(
            id_produto=1,
            id_usuario=user_gerente.id,
            tipo_movimentacao=TipoMovimentacao.ENTRADA,
            motivo=MotivoMovimentacao.REPOSICAO,
            quantidade=10,
        ),
        Movimentacao(
            id_produto=1,
            id_usuario=user_gerente.id,
            tipo_movimentacao=TipoMovimentacao.SAIDA,
            motivo=MotivoMovimentacao.AJUSTE,
            quantidade=3,
        ),
    ]

    mock_mov_repository.listar.return_value = movimentacoes

    resultado = estoque_service.listar_movimentacoes(user_gerente)

    assert resultado == movimentacoes
    mock_mov_repository.listar.assert_called_once()


def test_listar_movimentacoes_com_gerente(
    estoque_service, mock_mov_repository, user_gerente
):
    movimentacoes = [
        Movimentacao(
            id_produto=1,
            id_usuario=user_gerente.id,
            tipo_movimentacao=TipoMovimentacao.ENTRADA,
            motivo=MotivoMovimentacao.REPOSICAO,
            quantidade=5,
        )
    ]

    mock_mov_repository.listar.return_value = movimentacoes

    resultado = estoque_service.listar_movimentacoes(user_gerente)

    assert resultado == movimentacoes
    mock_mov_repository.listar.assert_called_once()


def test_listar_movimentacoes_sem_permissao(
    estoque_service, mock_mov_repository, user_funcionario
):
    user_funcionario.papel = PapelEnum.FUNCIONARIO
    with pytest.raises(PermissionError, match='Você não tem permissão'):
        estoque_service.listar_movimentacoes(user_funcionario)

    mock_mov_repository.listar.assert_not_called()


def test_validar_disponibilidade_com_estoque_suficiente(
    estoque_service, mock_product_repository, produto
):
    produto.quantidade = 10
    mock_product_repository.buscar_por_id.return_value = produto

    resultado = estoque_service.validar_disponibilidade(
        id_produto=produto.id, quantidade_desejada=5
    )

    assert resultado is True

    mock_product_repository.buscar_por_id.assert_called_once_with(produto.id)


def test_validar_disponibilidade_com_estoque_insuficiente(
    estoque_service, mock_product_repository, produto
):
    produto.quantidade = 10
    mock_product_repository.buscar_por_id.return_value = produto

    resultado = estoque_service.validar_disponibilidade(
        id_produto=produto.id, quantidade_desejada=11
    )

    assert resultado is False

    mock_product_repository.buscar_por_id.assert_called_once_with(produto.id)


def test_validar_disponibilidade_com_produto_inexistente(
    estoque_service, mock_product_repository
):
    mock_product_repository.buscar_por_id.return_value = None

    with pytest.raises(LookupError, match='Produto nao encontrado'):
        estoque_service.validar_disponibilidade(
            id_produto=999999, quantidade_desejada=5
        )


@pytest.mark.parametrize('papel', [PapelEnum.ADMIN, PapelEnum.GERENTE])
def test_relatorio_estoque_calcula_totais(
    estoque_service,
    mock_product_repository,
    mock_mov_repository,
    user_gerente,
    papel,
):
    user_gerente.papel = papel
    produtos = [
        criar_produto('TECLADO', Decimal('150.00'), 5, 1),
        criar_produto('MOUSE', Decimal('25.00'), 10, 2),
        criar_produto('CABO', Decimal('15.00'), 0, 3),
    ]
    mock_product_repository.listar.return_value = produtos

    relatorio = estoque_service.relatorio_estoque(user_gerente)

    assert isinstance(relatorio, RelatorioEstoqueResumo)
    assert relatorio.produtos == produtos
    assert relatorio.quantidade_produtos_cadastrados == len(produtos)
    assert relatorio.total_unidades_estoque == sum(
        produto.quantidade for produto in produtos
    )
    assert relatorio.quantidade_produtos_sem_estoque == 1
    assert [produto.quantidade for produto in produtos] == [5, 10, 0]

    mock_product_repository.listar.assert_called_once_with()
    mock_product_repository.atualizar.assert_not_called()
    mock_mov_repository.criar.assert_not_called()


def test_relatorio_estoque_sem_produtos(
    estoque_service, mock_product_repository, user_gerente
):
    mock_product_repository.listar.return_value = []

    relatorio = estoque_service.relatorio_estoque(user_gerente)

    assert isinstance(relatorio, RelatorioEstoqueResumo)
    assert relatorio.produtos == []
    assert relatorio.quantidade_produtos_cadastrados == 0
    assert relatorio.total_unidades_estoque == 0
    assert relatorio.quantidade_produtos_sem_estoque == 0


def test_relatorio_estoque_com_todos_os_produtos_zerados(
    estoque_service, mock_product_repository, user_gerente
):
    produtos = [
        criar_produto('TECLADO', Decimal('150.00'), 0, 1),
        criar_produto('MOUSE', Decimal('25.00'), 0, 2),
    ]
    mock_product_repository.listar.return_value = produtos

    relatorio = estoque_service.relatorio_estoque(user_gerente)

    assert relatorio.produtos == produtos
    assert relatorio.quantidade_produtos_cadastrados == len(produtos)
    assert relatorio.total_unidades_estoque == 0
    assert relatorio.quantidade_produtos_sem_estoque == len(produtos)


def test_relatorio_estoque_sem_permissao(
    estoque_service, mock_product_repository, user_funcionario
):
    user_funcionario.papel = PapelEnum.FUNCIONARIO

    with pytest.raises(PermissionError, match='Você não tem permissão'):
        estoque_service.relatorio_estoque(user_funcionario)

    mock_product_repository.listar.assert_not_called()


def test_relatorio_estoque_propaga_erro_da_consulta(
    estoque_service, mock_product_repository, user_gerente
):
    erro = RuntimeError('Erro ao consultar produtos')
    mock_product_repository.listar.side_effect = erro

    with pytest.raises(RuntimeError, match='Erro ao consultar produtos'):
        estoque_service.relatorio_estoque(user_gerente)


@pytest.mark.parametrize('papel', [PapelEnum.ADMIN, PapelEnum.GERENTE])
def test_relatorio_estoque_baixo_filtra_e_ordena(
    estoque_service,
    mock_product_repository,
    mock_mov_repository,
    user_gerente,
    papel,
):
    user_gerente.papel = papel
    produtos = [
        criar_produto('TECLADO', Decimal('150.00'), 5, 1),
        criar_produto('ADAPTADOR', Decimal('20.00'), 6, 2),
        criar_produto('CABO', Decimal('15.00'), 5, 3),
        criar_produto('MOUSE', Decimal('25.00'), 0, 4),
        criar_produto('PILHA', Decimal('5.00'), 2, 5),
    ]
    mock_product_repository.listar.return_value = produtos

    resultado = estoque_service.relatorio_estoque_baixo(user_gerente, 5)

    assert resultado == [produtos[3], produtos[4], produtos[2], produtos[0]]
    assert [produto.id for produto in produtos] == [1, 2, 3, 4, 5]
    assert [produto.quantidade for produto in produtos] == [5, 6, 5, 0, 2]

    mock_product_repository.listar.assert_called_once_with()
    mock_product_repository.atualizar.assert_not_called()
    mock_mov_repository.criar.assert_not_called()


def test_relatorio_estoque_baixo_com_limite_zero(
    estoque_service, mock_product_repository, user_gerente
):
    produto_zerado = criar_produto('CABO', Decimal('15.00'), 0, 1)
    produto_com_estoque = criar_produto('MOUSE', Decimal('25.00'), 1, 2)
    mock_product_repository.listar.return_value = [produto_com_estoque, produto_zerado]

    resultado = estoque_service.relatorio_estoque_baixo(user_gerente, 0)

    assert resultado == [produto_zerado]


def test_relatorio_estoque_baixo_sem_produtos(
    estoque_service, mock_product_repository, user_gerente
):
    mock_product_repository.listar.return_value = []

    resultado = estoque_service.relatorio_estoque_baixo(user_gerente, 5)

    assert resultado == []


def test_relatorio_estoque_baixo_sem_produtos_dentro_do_limite(
    estoque_service, mock_product_repository, user_gerente, produto
):
    produto.quantidade = 10
    mock_product_repository.listar.return_value = [produto]

    resultado = estoque_service.relatorio_estoque_baixo(user_gerente, 5)

    assert resultado == []


def test_relatorio_estoque_baixo_sem_permissao(
    estoque_service, mock_product_repository, user_funcionario
):
    user_funcionario.papel = PapelEnum.FUNCIONARIO

    with pytest.raises(PermissionError, match='Você não tem permissão'):
        estoque_service.relatorio_estoque_baixo(user_funcionario, 5)

    mock_product_repository.listar.assert_not_called()
