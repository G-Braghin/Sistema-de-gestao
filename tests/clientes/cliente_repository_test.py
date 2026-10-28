from tests.clientes.conftest import ClienteFatory


def test_criar_cliente_e_buscar_id(client_repository):
    cliente = ClienteFatory()
    cliente_criado = client_repository.criar(cliente)

    assert cliente_criado.id is not None

    response = client_repository.buscar_por_id(cliente_criado.id)

    assert response is not None
    assert response.ativo is True
    assert response.nome == cliente.nome
    assert response.cpf == cliente.cpf
    assert response.telefone == cliente.telefone
    assert response.endereco == cliente.endereco


def test_buscar_cliente_cpf(client_repository):
    cliente = ClienteFatory()
    cliente_criado = client_repository.criar(cliente)

    response = client_repository.buscar_por_cpf(cliente_criado.cpf)

    assert response is not None
    assert response.ativo is True
    assert response.nome == cliente.nome
    assert response.cpf == cliente.cpf
    assert response.telefone == cliente.telefone
    assert response.endereco == cliente.endereco


def test_atualizar_cliente(client_repository):
    cliente = ClienteFatory(nome='Bob', endereco='Rua A', telefone='45555555543')
    cliente_salvo = client_repository.criar(cliente)

    cliente_salvo.nome = 'Novo Bob'
    cliente_salvo.endereco = 'Rua B'
    cliente_salvo.telefone = '12123459532'

    client_repository.atualizar(cliente_salvo)

    response = client_repository.buscar_por_cpf(cliente_salvo.cpf)

    assert response.id == cliente_salvo.id
    assert response.nome == 'Novo Bob'
    assert response.telefone == '12123459532'
    assert response.endereco == 'Rua B'


def test_buscar_cliente_inexistente(client_repository):
    cliente_id = client_repository.buscar_por_id(9999999)
    cliente_cpf = client_repository.buscar_por_cpf('99999999999')

    assert cliente_id is None
    assert cliente_cpf is None


def test_listar_clientes_ativos(client_repository):
    cliente = ClienteFatory(ativo=True)

    client_repository.criar(cliente)

    clientes = client_repository.listar(True)

    assert any(c.id == cliente.id for c in clientes)


def test_listar_clientes_inativos(client_repository):
    cliente = ClienteFatory(ativo=False)

    client_repository.criar(cliente)

    clientes = client_repository.listar(False)

    assert any(c.id == cliente.id for c in clientes)
