from decimal import Decimal

import pytest


def test_validar_nome_valido(product_service):
    nome = 'Teclado'
    assert product_service.validar_nome(nome) is True


@pytest.mark.parametrize(
    'caso',
    [
        (''),
        ('  '),
        (None),
        ('AB'),
        ('A' * 61),
        ('Teclado@'),
        (123),
        ('Teclado\tMecanico'),
        ('Teclado\nMecanico'),
    ],
)
def test_validar_nome_com_dados_invalidos_retorna_falso(product_service, caso):
    nome = caso
    assert product_service.validar_nome(nome) is False


@pytest.mark.parametrize('caso', [(10), ('10.50')])
def test_validar_preco_valido_retorna_true(product_service, caso):
    preco = caso
    assert product_service.validar_preco(preco) is True


@pytest.mark.parametrize('caso', [('abc'), ('-10.50'), (0), ('10.999')])
def test_validar_preco_com_dados_invalido_retorna_falso(product_service, caso):
    preco = caso
    assert product_service.validar_preco(preco) is False


def test_cadastrar_produto_com_dados_validos_retorna_produto(
    product_service, product_repository_mock, produto
):
    product_repository_mock.criar.return_value = produto

    resultado = product_service.cadastrar_produto(
        nome='teclado mecanico',
        preco='150.50',
    )

    assert resultado == produto

    product_repository_mock.criar.assert_called_once()

    produto_enviado = product_repository_mock.criar.call_args.args[0]

    assert produto_enviado.nome == 'TECLADO MECANICO'
    assert produto_enviado.preco == Decimal('150.50')


@pytest.mark.parametrize(
    ('caso'),
    [
        ('AB', '150.50', 'O nome do produto e invalido!'),
        ('Teclado', '150.555', 'O preco do produto e invalido!'),
    ],
)
def test_cadastrar_produto_com_nome_invalido_da_erro(
    product_service, product_repository_mock, caso
):
    nome_produto, preco_produto, mensagem = caso
    with pytest.raises(ValueError, match=mensagem):
        product_service.cadastrar_produto(nome=nome_produto, preco=preco_produto)

    product_repository_mock.criar.assert_not_called()


def test_atualizar_preco_com_id_zero_da_erro(product_service, product_repository_mock):
    with pytest.raises(ValueError, match='ID de produto invalido'):
        product_service.atualizar_preco(0, '180.50')

    product_repository_mock.buscar_por_id_para_atualizar.assert_not_called()
    product_repository_mock.atualizar.assert_not_called()


def test_atualizar_nome_com_id_negativo_da_erro(
    product_service, product_repository_mock
):
    with pytest.raises(ValueError, match='ID de produto invalido'):
        product_service.atualizar_nome(-1, 'Teclado')

    product_repository_mock.buscar_por_id_para_atualizar.assert_not_called()
    product_repository_mock.atualizar.assert_not_called()


def test_listar_produtos_retorna_produto(
    product_service, product_repository_mock, produto
):
    product_repository_mock.listar.return_value = produto

    resultado = product_service.listar_produtos()

    assert resultado == produto
    product_repository_mock.listar.assert_called_once()


def test_listar_produtos_sem_produtos_retorna_nada(
    product_service, product_repository_mock
):
    product_repository_mock.listar.return_value = []

    resultado = product_service.listar_produtos()

    assert resultado == []
    product_repository_mock.listar.assert_called_once()


def test_atualizar_preco_com_dados_validos_retorna_produto(
    product_service, product_repository_mock, produto
):

    product_repository_mock.buscar_por_id_para_atualizar.return_value = produto
    product_repository_mock.atualizar.return_value = produto

    resultado = product_service.atualizar_preco(id_produto=1, preco='180.50')

    assert resultado == produto
    assert produto.preco == Decimal('180.50')

    product_repository_mock.buscar_por_id_para_atualizar.assert_called_once_with(1)
    product_repository_mock.atualizar.assert_called_once_with(produto)


def test_atualizar_preco_com_produto_inexistente_retorna_erro(
    product_service, product_repository_mock
):
    product_repository_mock.buscar_por_id_para_atualizar.return_value = None

    with pytest.raises(ValueError, match='Produto nao encontrado'):
        product_service.atualizar_preco(id_produto=999999, preco='180.50')

    product_repository_mock.atualizar.assert_not_called()


def test_atualizar_preco_invalido_retorna_erro(
    product_service, product_repository_mock, produto
):
    product_repository_mock.buscar_por_id_para_atualizar.return_value = produto

    with pytest.raises(ValueError, match='preco do produto'):
        product_service.atualizar_preco(produto.id, preco='180.555')

    product_repository_mock.atualizar.assert_not_called()


def test_atualizar_nome_com_dados_validos_retorna_produto(
    product_service, product_repository_mock, produto
):
    product_repository_mock.buscar_por_id_para_atualizar.return_value = produto
    product_repository_mock.atualizar.return_value = produto

    resultado = product_service.atualizar_nome(produto.id, nome=' teclado mecânico ')

    assert resultado == produto
    assert produto.nome == 'TECLADO MECÂNICO'

    product_repository_mock.buscar_por_id_para_atualizar.assert_called_once_with(
        produto.id
    )
    product_repository_mock.atualizar.assert_called_once_with(produto)


def test_atualizar_nome_com_produto_inexistente_retorna_erro(
    product_service, product_repository_mock
):
    product_repository_mock.buscar_por_id_para_atualizar.return_value = None

    with pytest.raises(ValueError, match='Produto nao encontrado'):
        product_service.atualizar_nome(id_produto=999999, nome='Teclado')

    product_repository_mock.atualizar.assert_not_called()


def test_atualizar_nome_invalido_retorna_erro(
    product_service, product_repository_mock, produto
):
    product_repository_mock.buscar_por_id_para_atualizar.return_value = produto

    with pytest.raises(ValueError, match='O nome do produto e invalido!'):
        product_service.atualizar_nome(produto.id, nome='AB')

    product_repository_mock.atualizar.assert_not_called()
