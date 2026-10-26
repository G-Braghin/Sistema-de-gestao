from unittest.mock import Mock

import pytest
from psycopg2 import OperationalError
from psycopg2.errors import UniqueViolation
from src.entities.cliente import Cliente
from src.entities.enums.papel_usuario import PapelUsuario
from src.entities.usuario import Usuario
from src.services.cliente_service import ClienteService


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def service(repository):
    return ClienteService(repository)


@pytest.fixture
def erro_unicidade():
    class ErroUnicidadeTeste(UniqueViolation):
        diag = Mock()

    return ErroUnicidadeTeste()


@pytest.fixture
def usuario_logado():
    return Usuario(
        id_usuario=1,
        nome="Gerente teste",
        senha_hash="hash_teste",
        papel=PapelUsuario.GERENTE,
    )


@pytest.fixture
def funcionario():
    return Usuario(
        id_usuario=2,
        nome="Funcionario teste",
        senha_hash="hash_teste",
        papel=PapelUsuario.FUNCIONARIO,
    )


def test_cadastrar_cliente_com_dados_validos(service, repository):
    repository.buscar_por_cpf.return_value = None

    cliente_criado = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A",
    )

    repository.criar.return_value = cliente_criado

    resultado = service.cadastrar_cliente(
        nome="João da Silva",
        cpf="529.982.247-25",
        telefone="(67) 99999-8888",
        endereco="Rua A",
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
            nome="   ", cpf="52998224725", telefone="67999998888", endereco="Rua A"
        )

    repository.criar.assert_not_called()


def test_cadastrar_cliente_com_cpf_vazio(service, repository):
    with pytest.raises(ValueError, match="CPF"):
        service.cadastrar_cliente(
            nome="João", cpf="", telefone="67999998888", endereco="Rua A"
        )

    repository.criar.assert_not_called()


def test_cadastrar_cliente_com_cpf_invalido(service, repository):
    with pytest.raises(ValueError, match="CPF"):
        service.cadastrar_cliente(
            nome="João", cpf="52998224724", telefone="67999998888", endereco="Rua A"
        )

    repository.criar.assert_not_called()


def test_cadastrar_cliente_com_cpf_ja_cadastrado(service, repository):
    repository.buscar_por_cpf.return_value = Cliente(
        id_cliente=1,
        nome="Cliente Existente",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A",
    )

    with pytest.raises(ValueError, match="CPF já está cadastrado"):
        service.cadastrar_cliente(
            nome="João", cpf="52998224725", telefone="67999998888", endereco="Rua B"
        )

    repository.criar.assert_not_called()


def test_cadastrar_cliente_com_cpf_duplicado_no_banco(
    service, repository, erro_unicidade
):
    repository.buscar_por_cpf.return_value = None
    erro_unicidade.diag.constraint_name = "clientes_cpf_unico"
    repository.criar.side_effect = erro_unicidade

    with pytest.raises(ValueError, match="CPF já está cadastrado"):
        service.cadastrar_cliente("João", "52998224725", "67999998888")

    repository.criar.assert_called_once()


def test_cadastrar_cliente_preserva_outra_violacao_de_unicidade(
    service, repository, erro_unicidade
):
    repository.buscar_por_cpf.return_value = None
    erro_unicidade.diag.constraint_name = "clientes_pkey"
    repository.criar.side_effect = erro_unicidade

    with pytest.raises(UniqueViolation) as erro:
        service.cadastrar_cliente("João", "52998224725", "67999998888")

    assert erro.value is erro_unicidade


def test_cadastrar_cliente_preserva_erro_de_conexao(service, repository):
    repository.buscar_por_cpf.return_value = None
    erro_conexao = OperationalError("Falha na conexao")
    repository.criar.side_effect = erro_conexao

    with pytest.raises(OperationalError) as erro:
        service.cadastrar_cliente("João", "52998224725", "67999998888")

    assert erro.value is erro_conexao


def test_cadastrar_cliente_com_telefone_vazio(service, repository):
    repository.buscar_por_cpf.return_value = None

    with pytest.raises(ValueError, match="telefone"):
        service.cadastrar_cliente(
            nome="João", cpf="52998224725", telefone="", endereco="Rua A"
        )

    repository.criar.assert_not_called()


def test_cadastrar_cliente_com_telefone_invalido(service, repository):
    repository.buscar_por_cpf.return_value = None

    with pytest.raises(ValueError, match="telefone"):
        service.cadastrar_cliente(
            nome="João", cpf="52998224725", telefone="6733338888", endereco="Rua A"
        )

    repository.criar.assert_not_called()


def test_atualizar_telefone_com_dados_validos(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A",
    )

    repository.buscar_por_cpf.return_value = cliente
    repository.atualizar.return_value = cliente

    resultado = service.atualizar_telefone(
        cpf_cliente="52998224725", telefone="(67) 98888-7777"
    )

    assert resultado == cliente
    assert cliente.telefone == "67988887777"

    repository.buscar_por_cpf.assert_called_once_with("52998224725")
    repository.atualizar.assert_called_once_with(cliente)


def test_atualizar_telefone_com_cliente_inexistente(service, repository):
    repository.buscar_por_cpf.return_value = None

    with pytest.raises(ValueError, match="Cliente nao encontrado."):
        service.atualizar_telefone(cpf_cliente="276.767.800-39", telefone="67999998888")

    repository.atualizar.assert_not_called()


def test_atualizar_telefone_vazio(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A",
    )

    repository.buscar_por_cpf.return_value = cliente

    with pytest.raises(ValueError, match="telefone"):
        service.atualizar_telefone(cpf_cliente="52998224725", telefone="")

    repository.atualizar.assert_not_called()


def test_atualizar_telefone_invalido(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A",
    )

    repository.buscar_por_cpf.return_value = cliente

    with pytest.raises(ValueError, match="telefone"):
        service.atualizar_telefone(cpf_cliente="52998224725", telefone="6733338888")

    repository.atualizar.assert_not_called()


def test_atualizar_telefone_cliente_desativado(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A",
        ativo=False,
    )
    repository.buscar_por_cpf.return_value = cliente

    with pytest.raises(ValueError, match="Cliente esta desativado."):
        service.atualizar_telefone(cpf_cliente="52998224725", telefone="6733338888")
    repository.atualizar.assert_not_called()


def test_atualizar_endereco_com_dados_validos(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco=None,
    )

    repository.buscar_por_cpf.return_value = cliente
    repository.atualizar.return_value = cliente

    resultado = service.atualizar_endereco(
        cpf_cliente="52998224725", endereco=" Rua A "
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
        endereco="Rua A",
    )

    repository.buscar_por_cpf.return_value = cliente
    repository.atualizar.return_value = cliente

    resultado = service.atualizar_endereco(cpf_cliente="52998224725", endereco="")

    assert resultado == cliente
    assert cliente.endereco == ""

    repository.atualizar.assert_called_once_with(cliente)


def test_atualizar_endereco_none(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A",
    )

    repository.buscar_por_cpf.return_value = cliente

    resultado = service.atualizar_endereco(cpf_cliente="52998224725", endereco=None)

    assert resultado == cliente
    assert cliente.endereco == "Rua A"

    repository.atualizar.assert_not_called()


def test_atualizar_endereco_com_cliente_inexistente(service, repository):
    repository.buscar_por_cpf.return_value = None

    with pytest.raises(ValueError, match="Cliente nao encontrado."):
        service.atualizar_endereco(cpf_cliente="276.767.800-39", endereco="Rua A")

    repository.atualizar.assert_not_called()


def test_atualizar_endereco_cliente_desativado(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco=None,
        ativo=False,
    )

    repository.buscar_por_cpf.return_value = cliente

    with pytest.raises(ValueError, match="Cliente esta desativado."):
        service.atualizar_endereco(cpf_cliente="52998224725", endereco="Rua A")
    repository.atualizar.assert_not_called()


def test_atualizar_nome_com_dados_validos(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Sil",
        cpf="52998224725",
        telefone="67999998888",
        endereco=None,
    )

    repository.buscar_por_cpf.return_value = cliente
    repository.atualizar.return_value = cliente

    resultado = service.atualizar_nome(cpf_cliente="52998224725", nome="João da Silva")

    assert resultado == cliente
    assert cliente.nome == "João da Silva"

    repository.buscar_por_cpf.assert_called_once_with("52998224725")
    repository.atualizar.assert_called_once_with(cliente)


def test_atualizar_nome_vazio(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A",
    )

    repository.buscar_por_cpf.return_value = cliente

    with pytest.raises(ValueError, match="O nome nao pode estar vazio."):
        service.atualizar_nome(cpf_cliente="52998224725", nome="")
    assert cliente.nome == "João da Silva"

    repository.atualizar.assert_not_called()


def test_atualizar_nome_none(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A",
    )

    repository.buscar_por_cpf.return_value = cliente

    with pytest.raises(ValueError, match="O nome nao pode estar vazio."):
        service.atualizar_nome(cpf_cliente="52998224725", nome=None)

    assert cliente.nome == "João da Silva"

    repository.atualizar.assert_not_called()


def test_atualizar_com_nome_com_cliente_inexistente(service, repository):
    repository.buscar_por_cpf.return_value = None

    with pytest.raises(ValueError, match="Cliente nao encontrado."):
        service.atualizar_nome(cpf_cliente="276.767.800-39", nome="João da Silva")

    repository.atualizar.assert_not_called()


def test_atualizar_nome_com_cliente_desativado(service, repository):
    cliente = Cliente(
        id_cliente=1,
        nome="João da Silva",
        cpf="52998224725",
        telefone="67999998888",
        endereco=None,
        ativo=False,
    )

    repository.buscar_por_cpf.return_value = cliente

    with pytest.raises(ValueError, match="Cliente esta desativado."):
        service.atualizar_nome(cpf_cliente="52998224725", nome="João da Silva")

    repository.atualizar.assert_not_called()


def test_listar_clientes_ativos(service, repository, funcionario):
    clientes = [
        Cliente(
            id_cliente=1,
            nome="João",
            cpf="52998224725",
            telefone="67999998888",
            endereco="Rua A",
            ativo=True,
        )
    ]

    repository.listar.return_value = clientes

    resultado = service.listar(funcionario, True)

    assert resultado == clientes
    repository.listar.assert_called_once_with(True)


def test_listar_clientes_inativos(service, repository, usuario_logado):
    repository.listar.return_value = []

    resultado = service.listar(usuario_logado, False)

    assert resultado == []
    repository.listar.assert_called_once_with(False)


def test_listar_cliente_desativados_funcionario(service, repository, funcionario):
    repository.listar.return_value = []

    with pytest.raises(
        PermissionError,
        match="Funcionarios nao tem permissao para ver cliente desativados.",
    ):
        service.listar(funcionario, False)

    repository.listar.assert_not_called()


def test_desativar_cliente(service, repository, usuario_logado):
    cliente = Cliente(
        id_cliente=1,
        nome="João",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A",
        ativo=True,
    )

    repository.buscar_por_id.return_value = cliente
    repository.atualizar.return_value = cliente

    resultado = service.atualizar_status(usuario_logado, 1, False)

    assert resultado.id_cliente == 1
    assert resultado.ativo == False

    repository.atualizar.assert_called_once_with(cliente)
    repository.buscar_por_id.assert_called_once_with(1)


def test_ativar_cliente(service, repository, usuario_logado):
    cliente = Cliente(
        id_cliente=1,
        nome="João",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A",
        ativo=False,
    )
    repository.buscar_por_id.return_value = cliente
    repository.atualizar.return_value = cliente

    resultado = service.atualizar_status(usuario_logado, 1, True)

    assert resultado.id_cliente == 1
    assert resultado.ativo == True

    repository.atualizar.assert_called_once_with(cliente)
    repository.buscar_por_id.assert_called_once_with(1)


def test_ativar_cliente_ativado(service, repository, usuario_logado):
    cliente = Cliente(
        id_cliente=1,
        nome="João",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A",
        ativo=True,
    )
    repository.buscar_por_id.return_value = cliente
    repository.atualizar.return_value = cliente

    with pytest.raises(ValueError, match="Cliente ja esta ativo"):
        service.atualizar_status(usuario_logado, 1, True)

    repository.atualizar.assert_not_called()


def test_desativar_cliente_desativado(service, repository, usuario_logado):
    cliente = Cliente(
        id_cliente=1,
        nome="João",
        cpf="52998224725",
        telefone="67999998888",
        endereco="Rua A",
        ativo=False,
    )
    repository.buscar_por_id.return_value = cliente
    repository.atualizar.return_value = cliente

    with pytest.raises(ValueError, match="Cliente ja esta desativado."):
        service.atualizar_status(usuario_logado, 1, False)

    repository.atualizar.assert_not_called()


def test_atualizar_status_cliente_inexistente(service, repository, usuario_logado):
    repository.buscar_por_id.return_value = None

    with pytest.raises(ValueError, match="Cliente nao encontrado"):
        service.atualizar_status(usuario_logado, 999999, True)

    repository.buscar_por_id.assert_called_once_with(999999)
    repository.atualizar.assert_not_called()


def test_atualizar_status_cliente_id_letras(service, repository, usuario_logado):
    repository.buscar_por_id.return_value = None

    with pytest.raises(TypeError, match="ID tem que ser um numero."):
        service.atualizar_status(usuario_logado, "abc", True)

    repository.buscar_por_id.assert_not_called()
    repository.atualizar.assert_not_called()


def test_atualizar_status_cliente_id_bool(service, repository, usuario_logado):
    repository.buscar_por_id.return_value = None

    with pytest.raises(TypeError, match="ID tem que ser um numero."):
        service.atualizar_status(usuario_logado, True, True)

    repository.buscar_por_id.assert_not_called()
    repository.atualizar.assert_not_called()


def test_atualizar_status_cliente_funcionario(service, repository, funcionario):
    repository.buscar_por_id.return_value = None

    with pytest.raises(
        PermissionError,
        match="Funcionarios nao tem permissao para atualizar status de clientes.",
    ):
        service.atualizar_status(funcionario, 1, True)

    repository.buscar_por_id.assert_not_called()
    repository.atualizar.assert_not_called()


def test_atualizar_status_cliente_nao_inserido(service, repository, usuario_logado):
    repository.buscar_por_id.return_value = None

    with pytest.raises(
        ValueError,
        match="ID nao inserido.",
    ):
        service.atualizar_status(usuario_logado, "", True)

    repository.buscar_por_id.assert_not_called()
    repository.atualizar.assert_not_called()
