import pytest
from faker import Faker

from tests.clientes.conftest import ClienteFatory, criar_client

faker = Faker('pt_BR')


def test_cadastrar_cliente_com_dados_validos(client_service, client_repository_mock):
    cliente_criado = criar_client()
    client_repository_mock.buscar_por_cpf.return_value = None
    client_repository_mock.criar.return_value = cliente_criado

    resultado = client_service.cadastrar_cliente(
        nome=cliente_criado.nome,
        cpf=cliente_criado.cpf,
        endereco=cliente_criado.endereco,
        telefone=cliente_criado.telefone,
    )

    assert resultado == cliente_criado

    client_repository_mock.criar.assert_called_once()

    cliente_enviado = client_repository_mock.criar.call_args.args[0]

    assert cliente_enviado.nome == resultado.nome
    assert cliente_enviado.cpf == resultado.cpf
    assert cliente_enviado.telefone == resultado.telefone
    assert cliente_enviado.endereco == resultado.endereco


@pytest.mark.parametrize(
    'caso',
    [
        (None, faker.ssn(), faker.cellphone_number(), 'O nome nao pode estar vazio.'),
        (faker.name(), None, faker.cellphone_number(), 'CPF nao pode estar vazio.'),
        (faker.name(), '11111111111', faker.cellphone_number(), 'CPF e invalido.'),
        (faker.name(), '52998224724', faker.cellphone_number(), 'CPF e invalido.'),
        (faker.name(), faker.ssn(), None, 'O telefone nao pode estar vazio.'),
        (faker.name(), faker.ssn(), '42234333234', 'O telefone e invalido!'),
    ],
)
def test_cadastrar_cliente_com_dados_invalidos(
    client_service, client_repository_mock, caso
):
    nome, cpf, telefone, mensagem = caso
    client_repository_mock.buscar_por_cpf.return_value = None

    with pytest.raises(ValueError, match=mensagem):
        client_service.cadastrar_cliente(
            nome=nome, cpf=cpf, telefone=telefone, endereco='Rua A'
        )

    client_repository_mock.criar.assert_not_called()


def test_cadastrar_cliente_com_cpf_ja_cadastrado(
    client_service, client_repository_mock
):
    cliente_cadastrado = criar_client()

    client_repository_mock.buscar_por_cpf.return_value = cliente_cadastrado

    with pytest.raises(ValueError, match='CPF já está cadastrado'):
        client_service.cadastrar_cliente(
            nome='Bob',
            cpf=cliente_cadastrado.cpf,
            telefone='67999998888',
            endereco='Rua B',
        )

    client_repository_mock.criar.assert_not_called()


@pytest.mark.parametrize(
    ('campo', 'valor'),
    [
        ('nome', 'Bob'),
        ('telefone', '55999932211'),
        ('endereco', faker.address()),
    ],
)
def test_atualizar_cliente_com_dados_validos(
    client_service, client_repository_mock, campo, valor
):
    cliente = criar_client()

    client_repository_mock.buscar_por_cpf.return_value = cliente
    client_repository_mock.atualizar.return_value = cliente

    resultado = client_service.atualizar(cpf_cliente=cliente.cpf, **{campo: valor})

    assert resultado == cliente
    assert getattr(resultado, campo) == valor

    client_repository_mock.buscar_por_cpf.assert_called_once_with(cliente.cpf)
    client_repository_mock.atualizar.assert_called_once_with(cliente)


@pytest.mark.parametrize(
    ('existe', 'ativo', 'dados', 'mensagem'),
    [
        (False, True, {'nome': 'Bob'}, 'Cliente nao encontrado.'),
        (True, False, {'nome': 'Bob'}, 'Cliente esta desativado.'),
        (True, True, {'telefone': ''}, 'Telefone invalido.'),
        (True, True, {'telefone': '66699932211'}, 'Telefone invalido.'),
    ],
)
def test_atualizar_cliente_com_dados_invalidos(
    client_service, client_repository_mock, existe, ativo, dados, mensagem
):
    cliente = criar_client(ativo=ativo)

    client_repository_mock.buscar_por_cpf.return_value = cliente if existe else None

    with pytest.raises(ValueError, match=mensagem):
        client_service.atualizar(cpf_cliente=cliente.cpf, **dados)

    client_repository_mock.atualizar.assert_not_called()


def test_listar_clientes_ativos(
    client_service, client_repository_mock, user_funcionario
):
    numero_esperado = 5
    clientes = ClienteFatory.build_batch(numero_esperado, ativo=True)

    client_repository_mock.listar.return_value = clientes

    resultado = client_service.listar(user_funcionario, True)

    assert resultado == clientes
    assert len(resultado) == numero_esperado
    client_repository_mock.listar.assert_called_once_with(True)


def test_listar_clientes_inativos_gerente(
    client_service, client_repository_mock, user_gerente
):
    numero_esperado = 5
    clientes = ClienteFatory.build_batch(numero_esperado, ativo=False)

    client_repository_mock.listar.return_value = clientes

    resultado = client_service.listar(user_gerente, False)

    assert resultado == clientes
    assert len(resultado) == numero_esperado
    client_repository_mock.listar.assert_called_once_with(False)


def test_listar_clientes_desativados_funcionario(
    client_service, client_repository_mock, user_funcionario
):
    client_repository_mock.listar.return_value = []

    with pytest.raises(
        PermissionError,
        match='Funcionarios nao tem permissao para ver cliente desativados.',
    ):
        client_service.listar(user_funcionario, False)

    client_repository_mock.listar.assert_not_called()


def test_desativar_cliente_ativo(
    client_service, client_repository_mock, cliente, user_gerente
):
    client_repository_mock.buscar_por_id.return_value = cliente
    client_repository_mock.atualizar.return_value = cliente

    resultado = client_service.atualizar_status(user_gerente, cliente.id, False)

    assert resultado.id == cliente.id
    assert not resultado.ativo

    client_repository_mock.atualizar.assert_called_once_with(cliente)
    client_repository_mock.buscar_por_id.assert_called_once_with(cliente.id)


def test_ativar_cliente_desativado(
    client_service, client_repository_mock, cliente_inativo, user_gerente
):
    client_repository_mock.buscar_por_id.return_value = cliente_inativo
    client_repository_mock.atualizar.return_value = cliente_inativo

    resultado = client_service.atualizar_status(user_gerente, cliente_inativo.id, True)

    assert resultado.id == cliente_inativo.id
    assert resultado.ativo

    client_repository_mock.atualizar.assert_called_once_with(cliente_inativo)
    client_repository_mock.buscar_por_id.assert_called_once_with(cliente_inativo.id)


def test_ativar_cliente_ativo(
    client_service, client_repository_mock, cliente, user_gerente
):

    client_repository_mock.buscar_por_id.return_value = cliente
    client_repository_mock.atualizar.return_value = cliente

    with pytest.raises(ValueError, match='Cliente ja esta ativo'):
        client_service.atualizar_status(user_gerente, cliente.id, True)

    client_repository_mock.atualizar.assert_not_called()


def test_desativar_cliente_inativo(
    client_service, client_repository_mock, cliente_inativo, user_gerente
):

    client_repository_mock.buscar_por_id.return_value = cliente_inativo
    client_repository_mock.atualizar.return_value = cliente_inativo

    with pytest.raises(ValueError, match='Cliente ja esta desativado.'):
        client_service.atualizar_status(user_gerente, cliente_inativo.id, False)

    client_repository_mock.atualizar.assert_not_called()


def test_atualizar_status_cliente_inexistente(
    client_service, client_repository_mock, user_gerente
):
    client_repository_mock.buscar_por_id.return_value = None

    with pytest.raises(ValueError, match='Cliente nao encontrado'):
        client_service.atualizar_status(user_gerente, 999999, True)

    client_repository_mock.buscar_por_id.assert_called_once_with(999999)
    client_repository_mock.atualizar.assert_not_called()


def test_atualizar_status_cliente_funcionario(
    client_service, client_repository_mock, user_funcionario
):
    client_repository_mock.buscar_por_id.return_value = None

    with pytest.raises(
        PermissionError,
        match='Funcionarios nao tem permissao para atualizar status de clientes.',
    ):
        client_service.atualizar_status(user_funcionario, 1, True)

    client_repository_mock.buscar_por_id.assert_not_called()
    client_repository_mock.atualizar.assert_not_called()


def test_atualizar_status_cliente_nao_inserido(
    client_service, client_repository_mock, user_gerente
):
    client_repository_mock.buscar_por_id.return_value = None

    with pytest.raises(
        ValueError,
        match='ID nao inserido.',
    ):
        client_service.atualizar_status(user_gerente, '', True)

    client_repository_mock.buscar_por_id.assert_not_called()
    client_repository_mock.atualizar.assert_not_called()
