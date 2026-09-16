import pytest

from src.database.conexao import Conexao
from src.entities.cliente import Cliente
from src.repositories.cliente_repository import ClienteRepository


@pytest.fixture
def repository():
    conexao = Conexao()
    repository = ClienteRepository(conexao)

    yield repository

    conn = conexao.get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM clientes WHERE nome LIKE 'TESTE_%'"
        )
    conn.commit()

def test_criar_cliente_e_buscar_id(repository):
    cliente = Cliente(
        nome="TESTE_NOME",
        cpf="11111111111",
        telefone="(11) 1234-5678",
        endereco="teste endereco"
    )   
    cliente_criado=repository.criar(cliente)

    assert cliente_criado.id_cliente is not None

    cliente_buscado=repository.buscar_por_id(
        cliente_criado.id_cliente
    )

    assert cliente_buscado is not None
    assert cliente_buscado.nome == "TESTE_NOME"
    assert cliente_buscado.cpf == "11111111111"
    assert cliente_buscado.telefone == "(11) 1234-5678"
    assert cliente_buscado.endereco == "teste endereco"


def test_buscar_cliente_cpf(repository):
    cliente = Cliente(
            nome="TESTE_NOME",
            cpf="11111111111",
            telefone="(11) 1234-5678",
            endereco="teste endereco"
        )   
    cliente_criado=repository.criar(cliente)

    cliente_buscado= repository.buscar_por_cpf(
        cliente_criado.cpf
    )

    assert cliente_buscado is not None
    assert cliente_buscado.nome == "TESTE_NOME"
    assert cliente_buscado.cpf == "11111111111"
    assert cliente_buscado.telefone == "(11) 1234-5678"
    assert cliente_buscado.endereco == "teste endereco"

def test_atualizar_cliente(repository):
    cliente = Cliente(
                nome="TESTE_NOME",
                cpf="11111111111",
                telefone="(11) 1234-5678",
                endereco="teste endereco"
            )   
    cliente_salvo = repository.criar(cliente)

    cliente_salvo.nome = "TESTE_NOVO_NOME"
    cliente_salvo.telefone = "(22) 4321-8765"
    cliente_salvo.endereco = "Novo endereco teste"

    repository.atualizar(cliente_salvo)

    cliente_atualizado = repository.buscar_por_cpf(
        cliente_salvo.cpf
    )

    assert cliente_atualizado.id_cliente == cliente_salvo.id_cliente
    assert cliente_atualizado.nome == "TESTE_NOVO_NOME"
    assert cliente_atualizado.telefone == "(22) 4321-8765"
    assert cliente_atualizado.endereco == "Novo endereco teste"



def test_buscar_cliente_inexistente(repository):
    cliente_id = repository.buscar_por_id(9999999)
    cliente_cpf = repository.buscar_por_cpf("99999999999")

    assert cliente_id is None
    assert cliente_cpf is None


def test_atualizar_cliente_inexistente(repository):
    cliente = Cliente(
        id_cliente=9999999,
        nome="TESTE_NOME",
        cpf="11111111111",
        telefone="(11) 1234-5678",
        endereco="teste endereco"
    )

    with pytest.raises(ValueError):
        repository.atualizar(cliente)