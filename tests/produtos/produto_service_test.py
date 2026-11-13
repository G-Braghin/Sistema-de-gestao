from decimal import Decimal

import pytest


def test_cadastrar_produto_com_dados_validos_retorna_produto(
    product_service, product_repository_mock, produto
):
    product_repository_mock.criar.return_value = produto

    resultado = product_service.cadastrar_produto(
        nome='teclado mecanico',
        preco=Decimal('150.50'),
    )

    assert resultado == produto

    product_repository_mock.criar.assert_called_once()

    produto_enviado = product_repository_mock.criar.call_args.args[0]

    assert produto_enviado.nome == 'teclado mecanico'
    assert produto_enviado.preco == Decimal('150.50')


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


def test_atualizar_info_com_dados_validos_retorna_produto(
    product_service, product_repository_mock, produto
):

    product_repository_mock.buscar_por_id_para_atualizar.return_value = produto
    product_repository_mock.atualizar.return_value = produto

    resultado = product_service.atualizar(
        id_produto=1, preco=Decimal('180.50'), nome='Teclado'
    )

    assert resultado == produto
    assert produto.preco == Decimal('180.50')
    assert produto.nome == 'Teclado'

    product_repository_mock.buscar_por_id_para_atualizar.assert_called_once_with(1)
    product_repository_mock.atualizar.assert_called_once_with(produto)


def test_atualizar_info_produto_inexistente_retorna_erro(
    product_service, product_repository_mock
):
    product_repository_mock.buscar_por_id_para_atualizar.return_value = None

    with pytest.raises(LookupError, match='Produto nao encontrado'):
        product_service.atualizar(id_produto=999999, nome='Teclado')

    product_repository_mock.atualizar.assert_not_called()
