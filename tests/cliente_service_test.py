import pytest
from unittest.mock import Mock

from src.entities.cliente import Cliente
from src.services.cliente_service import ClienteService


@pytest.fixture
def repository():
    return Mock()

@pytest.fixture
def service(repository):
    return ClienteService(repository)


def test_validar_cpf_valido(service):
    assert service.validar_cpf("52998224725") is True


def test_validar_cpf_com_quantidade_invalida_de_digitos(service):
    assert service.validar_cpf("123456789") is False


def test_validar_cpf_com_digitos_repetidos(service):
    assert service.validar_cpf("11111111111") is False


def test_validar_cpf_invalido(service):
    assert service.validar_cpf("52998224724") is False


def test_validar_telefone_valido(service):
    assert service.validar_telefone("67999998888") is True


def test_validar_telefone_invalido(service):
    assert service.validar_telefone("6733338888") is False


def test_cadastrar_cliente_com_dados_validos(service, repository):
    repository.buscar_por_cpf.return_value = None

    cliente_criado = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A"
    )

    repository.criar.return_value = cliente_criado

    resultado = service.cadastrar_cliente(
        nome="João da Silva",
        cpf="529.982.247-25",
        telefone="(67) 99999-8888",
        endereco="Rua A"
    )

    assert resultado == cliente_criado

    repository.criar.assert_called_once()

    cliente_enviado = repository.criar.call_args.args[0]

    assert cliente_enviado.nome == "João da Silva"
    assert cliente_enviado.cpf == "52998224725"
    assert cliente_enviado.telefone == "67999998888"
    assert cliente_enviado.endereco == "Rua A"


def test_cadastrar_cliente_com_nome_vazio(service, repository):
    with pytest.raises(ValueError, match="nome"):
        service.cadastrar_cliente(
            nome="   ",
            cpf="52998224725",
            telefone="67999998888",
            endereco="Rua A"
        )

    repository.criar.assert_not_called()


def test_cadastrar_cliente_com_cpf_vazio(service, repository):
    with pytest.raises(ValueError, match="CPF"):
        service.cadastrar_cliente(
            nome="João",
            cpf="",
            telefone="67999998888",
            endereco="Rua A"
        )

    repository.criar.assert_not_called()


def test_cadastrar_cliente_com_cpf_invalido(service, repository):
    with pytest.raises(ValueError, match="CPF"):
        service.cadastrar_cliente(
            nome="João",
            cpf="52998224724",
            telefone="67999998888",
            endereco="Rua A"
        )

    repository.criar.assert_not_called()


def test_cadastrar_cliente_com_cpf_ja_cadastrado(service, repository):
    repository.buscar_por_cpf.return_value = Cliente(
        id_cliente=1,
        nome="Cliente Existente",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A"
    )

    with pytest.raises(ValueError, match="CPF já está cadastrado"):
        service.cadastrar_cliente(
            nome="João",
            cpf="52998224725",
            telefone="67999998888",
            endereco="Rua B"
        )

    repository.criar.assert_not_called()


def test_cadastrar_cliente_com_telefone_vazio(service, repository):
    repository.buscar_por_cpf.return_value = None

    with pytest.raises(ValueError, match="telefone"):
        service.cadastrar_cliente(
            nome="João",
            cpf="52998224725",
            telefone="",
            endereco="Rua A"
        )

    repository.criar.assert_not_called()


def test_cadastrar_cliente_com_telefone_invalido(service, repository):
    repository.buscar_por_cpf.return_value = None

    with pytest.raises(ValueError, match="telefone"):
        service.cadastrar_cliente(
            nome="João",
            cpf="52998224725",
            telefone="6733338888",
            endereco="Rua A"
        )

    repository.criar.assert_not_called()


def test_atualizar_telefone_com_dados_validos(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A"
    )

    repository.buscar_por_cpf.return_value = cliente
    repository.atualizar.return_value = cliente

    resultado = service.atualizar_telefone(
        cpf_cliente="52998224725",
        telefone="(67) 98888-7777"
    )

    assert resultado == cliente
    assert cliente.telefone == "67988887777"

    repository.buscar_por_cpf.assert_called_once_with("52998224725")
    repository.atualizar.assert_called_once_with(cliente)


def test_atualizar_telefone_com_cliente_inexistente(service, repository):
    repository.buscar_por_cpf.return_value = None

    with pytest.raises(ValueError, match="Cliente"):
        service.atualizar_telefone(
            cpf_cliente="99999999999",
            telefone="67999998888"
        )

    repository.atualizar.assert_not_called()


def test_atualizar_telefone_vazio(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A"
    )

    repository.buscar_por_cpf.return_value = cliente

    with pytest.raises(ValueError, match="telefone"):
        service.atualizar_telefone(
            cpf_cliente="52998224725",
            telefone=""
        )

    repository.atualizar.assert_not_called()


def test_atualizar_telefone_invalido(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A"
    )

    repository.buscar_por_cpf.return_value = cliente

    with pytest.raises(ValueError, match="telefone"):
        service.atualizar_telefone(
            cpf_cliente="52998224725",
            telefone="6733338888"
        )

    repository.atualizar.assert_not_called()


def test_atualizar_endereco_com_dados_validos(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco=None
    )

    repository.buscar_por_cpf.return_value = cliente
    repository.atualizar.return_value = cliente

    resultado = service.atualizar_endereco(
        cpf_cliente="52998224725",
        endereco=" Rua A "
    )

    assert resultado == cliente
    assert cliente.endereco == "Rua A"

    repository.buscar_por_cpf.assert_called_once_with("52998224725")
    repository.atualizar.assert_called_once_with(cliente)


def test_atualizar_endereco_vazio(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A"
    )

    repository.buscar_por_cpf.return_value = cliente
    repository.atualizar.return_value = cliente

    resultado = service.atualizar_endereco(
        cpf_cliente="52998224725",
        endereco=""
    )

    assert resultado == cliente
    assert cliente.endereco == ""

    repository.atualizar.assert_called_once_with(cliente)


def test_atualizar_endereco_none(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A"
    )

    repository.buscar_por_cpf.return_value = cliente

    resultado = service.atualizar_endereco(
        cpf_cliente="52998224725",
        endereco=None
    )

    assert resultado == cliente
    assert cliente.endereco == "Rua A"

    repository.atualizar.assert_not_called()


def test_atualizar_endereco_com_cliente_inexistente(service, repository):
    repository.buscar_por_cpf.return_value = None

    with pytest.raises(ValueError, match="Cliente"):
        service.atualizar_endereco(
            cpf_cliente="99999999999",
            endereco="Rua A"
        )

    repository.atualizar.assert_not_called()