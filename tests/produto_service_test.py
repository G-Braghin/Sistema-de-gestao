from decimal import Decimal
from unittest.mock import MagicMock, Mock

import pytest
from src.entities.produto import Produto
from src.services.produto_service import ProdutoService


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def conexao():
    conexao = Mock()
    conexao.get_connection.return_value = MagicMock()
    return conexao


@pytest.fixture
def service(repository, conexao):
    return ProdutoService(repository, conexao)


def test_validar_nome_valido(service):
    assert service.validar_nome("Teclado Mecânico") is True


def test_atualizar_preco_com_id_zero(service, repository, conexao):
    with pytest.raises(ValueError, match="ID de produto invalido"):
        service.atualizar_preco(0, "180.50")

    repository.buscar_por_id.assert_not_called()
    repository.atualizar.assert_not_called()
    conexao.get_connection.assert_not_called()


def test_atualizar_nome_com_id_negativo(service, repository, conexao):
    with pytest.raises(ValueError, match="ID de produto invalido"):
        service.atualizar_nome(-1, "Teclado")

    repository.buscar_por_id.assert_not_called()
    repository.atualizar.assert_not_called()
    conexao.get_connection.assert_not_called()


def test_atualizar_marca_com_id_booleano(service, repository, conexao):
    with pytest.raises(TypeError, match="ID tem que ser um numero inteiro"):
        service.atualizar_marca(True, "Logitech")

    repository.buscar_por_id.assert_not_called()
    repository.atualizar.assert_not_called()
    conexao.get_connection.assert_not_called()


def test_validar_nome_muito_curto(service):
    assert service.validar_nome("AB") is False


def test_validar_nome_muito_longo(service):
    nome = "A" * 61

    assert service.validar_nome(nome) is False


def test_validar_nome_com_caractere_invalido(service):
    assert service.validar_nome("Teclado@") is False


def test_validar_nome_vazio(service):
    assert service.validar_nome("") is False


def test_validar_nome_com_apenas_espacos(service):
    assert service.validar_nome("   ") is False


def test_validar_nome_none(service):
    assert service.validar_nome(None) is False


def test_validar_nome_numerico(service):
    assert service.validar_nome(123) is False


def test_validar_nome_com_tabulacao(service):
    assert service.validar_nome("Teclado\tMecanico") is False


def test_validar_nome_com_quebra_de_linha(service):
    assert service.validar_nome("Teclado\nMecanico") is False


def test_validar_preco_valido(service):
    assert service.validar_preco("10.50") is True


def test_validar_preco_inteiro(service):
    assert service.validar_preco(10) is True


def test_validar_preco_zero(service):
    assert service.validar_preco(0) is False


def test_validar_preco_negativo(service):
    assert service.validar_preco("-10.50") is False


def test_validar_preco_com_mais_de_duas_casas(service):
    assert service.validar_preco("10.555") is False


def test_validar_preco_com_texto_invalido(service):
    assert service.validar_preco("abc") is False


def test_cadastrar_produto_com_dados_validos(service, repository):
    produto_criado = Produto(
        id_produto=1,
        nome="TECLADO MECÂNICO",
        marca="LOGITECH",
        preco="150.60"
    )

    repository.criar.return_value = produto_criado

    resultado = service.cadastrar_produto(
        nome=" teclado mecânico ",
        marca=" logitech ",
        preco="150.60"
    )

    assert resultado == produto_criado

    repository.criar.assert_called_once()

    produto_enviado = repository.criar.call_args.args[0]

    assert produto_enviado.nome == "TECLADO MECÂNICO"
    assert produto_enviado.marca == "LOGITECH"
    assert produto_enviado.preco == Decimal("150.60")
    assert produto_enviado.quantidade_estoque == 0


def test_cadastrar_produto_com_nome_invalido(service, repository):
    with pytest.raises(ValueError, match="nome do produto"):
        service.cadastrar_produto(
            nome="AB",
            marca="LOGITECH",
            preco="150.60"
        )

    repository.criar.assert_not_called()


def test_cadastrar_produto_com_marca_invalida(service, repository):
    with pytest.raises(ValueError, match="marca do produto"):
        service.cadastrar_produto(
            nome="Teclado",
            marca="AB",
            preco="150.60"
        )

    repository.criar.assert_not_called()


def test_cadastrar_produto_com_preco_invalido(service, repository):
    with pytest.raises(ValueError, match="preco do produto"):
        service.cadastrar_produto(
            nome="Teclado",
            marca="Logitech",
            preco="10.555"
        )

    repository.criar.assert_not_called()


def test_listar_produtos(service, repository):
    produtos = [
        Produto(
            id_produto=1,
            nome="TECLADO",
            marca="LOGITECH",
            preco="150.00"
        ),
        Produto(
            id_produto=2,
            nome="MOUSE",
            marca="LOGITECH",
            preco="80.00"
        )
    ]

    repository.listar.return_value = produtos

    resultado = service.listar_produtos()

    assert resultado == produtos
    repository.listar.assert_called_once()


def test_listar_produtos_sem_produtos(service, repository):
    repository.listar.return_value = []

    resultado = service.listar_produtos()

    assert resultado == []
    repository.listar.assert_called_once()


def test_atualizar_preco_com_dados_validos(service, repository):
    produto = Produto(
        id_produto=1,
        nome="TECLADO",
        marca="LOGITECH",
        preco="150.00"
    )

    repository.buscar_por_id.return_value = produto
    repository.atualizar.return_value = produto

    resultado = service.atualizar_preco(
        id_produto=1,
        preco="180.50"
    )

    assert resultado == produto
    assert produto.preco == Decimal("180.50")

    repository.buscar_por_id.assert_called_once_with(1)
    repository.atualizar.assert_called_once_with(produto)


def test_atualizar_preco_com_produto_inexistente(service, repository):
    repository.buscar_por_id.return_value = None

    with pytest.raises(ValueError, match="Produto nao encontrado"):
        service.atualizar_preco(
            id_produto=999999,
            preco="180.50"
        )

    repository.atualizar.assert_not_called()


def test_atualizar_preco_invalido(service, repository):
    produto = Produto(
        id_produto=1,
        nome="TECLADO",
        marca="LOGITECH",
        preco="150.00"
    )

    repository.buscar_por_id.return_value = produto

    with pytest.raises(ValueError, match="preco do produto"):
        service.atualizar_preco(
            id_produto=1,
            preco="180.555"
        )

    repository.atualizar.assert_not_called()


def test_atualizar_nome_com_dados_validos(service, repository):
    produto = Produto(
        id_produto=1,
        nome="TECLADO",
        marca="LOGITECH",
        preco="150.00"
    )

    repository.buscar_por_id.return_value = produto
    repository.atualizar.return_value = produto

    resultado = service.atualizar_nome(
        id_produto=1,
        nome=" teclado mecânico "
    )

    assert resultado == produto
    assert produto.nome == "TECLADO MECÂNICO"

    repository.buscar_por_id.assert_called_once_with(1)
    repository.atualizar.assert_called_once_with(produto)


def test_atualizar_nome_com_produto_inexistente(service, repository):
    repository.buscar_por_id.return_value = None

    with pytest.raises(ValueError, match="Produto nao encontrado"):
        service.atualizar_nome(
            id_produto=999999,
            nome="Teclado"
        )

    repository.atualizar.assert_not_called()


def test_atualizar_nome_invalido(service, repository):
    produto = Produto(
        id_produto=1,
        nome="TECLADO",
        marca="LOGITECH",
        preco="150.00"
    )

    repository.buscar_por_id.return_value = produto

    with pytest.raises(ValueError, match="nome do produto"):
        service.atualizar_nome(
            id_produto=1,
            nome="AB"
        )

    repository.atualizar.assert_not_called()


def test_atualizar_marca_com_dados_validos(service, repository):
    produto = Produto(
        id_produto=1,
        nome="TECLADO",
        marca="LOGITECH",
        preco="150.00"
    )

    repository.buscar_por_id.return_value = produto
    repository.atualizar.return_value = produto

    resultado = service.atualizar_marca(
        id_produto=1,
        marca=" redragon "
    )

    assert resultado == produto
    assert produto.marca == "REDRAGON"

    repository.buscar_por_id.assert_called_once_with(1)
    repository.atualizar.assert_called_once_with(produto)


def test_atualizar_marca_com_produto_inexistente(service, repository):
    repository.buscar_por_id.return_value = None

    with pytest.raises(ValueError, match="Produto nao encontrado"):
        service.atualizar_marca(
            id_produto=999999,
            marca="Logitech"
        )

    repository.atualizar.assert_not_called()


def test_atualizar_marca_invalida(service, repository):
    produto = Produto(
        id_produto=1,
        nome="TECLADO",
        marca="LOGITECH",
        preco="150.00"
    )

    repository.buscar_por_id.return_value = produto

    with pytest.raises(ValueError, match="marca do produto"):
        service.atualizar_marca(
            id_produto=1,
            marca="AB"
        )

    repository.atualizar.assert_not_called()


def test_cadastrar_produto_finaliza_transacao(service, repository, conexao):
    conn = conexao.get_connection.return_value

    resultado = service.cadastrar_produto("Teclado", "Logitech", "150.00")

    assert resultado == repository.criar.return_value
    conn.__enter__.assert_called_once()
    conn.__exit__.assert_called_once_with(None, None, None)


def test_cadastrar_produto_propaga_erro_na_transacao(service, repository, conexao):
    conn = conexao.get_connection.return_value
    erro = RuntimeError("Erro ao salvar produto")
    repository.criar.side_effect = erro

    with pytest.raises(RuntimeError, match="Erro ao salvar produto"):
        service.cadastrar_produto("Teclado", "Logitech", "150.00")

    conn.__enter__.assert_called_once()
    conn.__exit__.assert_called_once()
    assert conn.__exit__.call_args.args[0] is RuntimeError
    assert conn.__exit__.call_args.args[1] is erro
