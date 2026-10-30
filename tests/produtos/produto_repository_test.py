from decimal import Decimal

from tests.produtos.conftest import ProductFactory


def test_criar_produto_e_buscar_id_retorna_produto(product_repository):
    produto = ProductFactory()
    produto_criado = product_repository.criar(produto)

    assert produto_criado.id is not None

    resultado = product_repository.buscar_por_id(produto_criado.id)

    assert resultado is not None
    assert resultado.id == produto_criado.id
    assert resultado.nome == produto_criado.nome
    assert resultado.preco == produto_criado.preco
    assert resultado.quantidade == produto_criado.quantidade


def test_buscar_por_id_atualizar_retorna_produto(product_repository, produto_db):
    resultado = product_repository.buscar_por_id_para_atualizar(produto_db.id)

    assert resultado is not None
    assert resultado.id == produto_db.id


def test_buscar_por_multiplos_ids_retorna_produtos(product_repository, produtos_db):
    ids = [produto.id for produto in produtos_db]
    tamanho_esperado = 2
    resultado = product_repository.buscar_por_multiplos_ids(lista_ids=[ids[2], ids[1]])

    resultado_ids = [produto.id for produto in resultado]

    assert len(resultado_ids) == tamanho_esperado
    assert ids[1] in resultado_ids
    assert ids[2] in resultado_ids
    assert ids[0] not in resultado_ids


def test_buscar_produto_inexistente_retorna_none(product_repository):
    id_inexistente = 9999999
    resultado = product_repository.buscar_por_id(id_inexistente)

    assert resultado is None


def test_buscar_produto_atulaizar_retorna_none(product_repository):
    id_inexistente = 9999999
    resultado = product_repository.buscar_por_id_para_atualizar(id_inexistente)

    assert resultado is None


def test_buscar_multiplos_lista_ids_inexistentes_retorna_nada(product_repository):
    ids_inexistentes = [9999, 99999, 999999]
    resultado = product_repository.buscar_por_multiplos_ids(ids_inexistentes)

    assert resultado == []


def test_listar_produto_retona_produtos(product_repository, produtos_db):

    resultado = product_repository.listar()

    assert len(resultado) == len(produtos_db)

    for produto in resultado:
        assert produto in produtos_db


def test_atualizar_produto_retorna_produto_atualizado(product_repository, produto_db):

    novo_preco = Decimal('1211.55')
    nova_quantidade = 8

    produto_db.nome = 'Novo nome'
    produto_db.preco = novo_preco
    produto_db.quantidade = nova_quantidade

    atualizado = product_repository.atualizar(produto_db)

    assert atualizado == produto_db

    resultado = product_repository.buscar_por_id(produto_db.id)

    assert resultado is not None
    assert resultado.nome == 'Novo nome'
    assert resultado.preco == novo_preco
    assert resultado.quantidade == nova_quantidade
