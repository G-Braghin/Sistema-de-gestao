import pytest

from src.database.conexao import Conexao
from src.entities.usuario import Usuario
from src.entities.enums.papel_usuario import PapelUsuario
from src.repositories.usuario_repository import UsuarioRepository


@pytest.fixture
def repository():
    conexao = Conexao()
    repository = UsuarioRepository(conexao)

    yield repository

    conn = conexao.get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM usuarios WHERE nome LIKE 'TESTE_%'"
        )

    conn.commit()


def test_criar_e_buscar_usuario(repository):
    usuario = Usuario(
        nome="TESTE_USUARIO",
        senha_hash="hash_teste",
        papel=PapelUsuario.FUNCIONARIO
    )

    usuario_criado = repository.criar(usuario)

    assert usuario_criado.id_usuario is not None

    usuario_buscado = repository.buscar_por_id(
        usuario_criado.id_usuario
    )

    assert usuario_buscado is not None
    assert usuario_buscado.nome == "TESTE_USUARIO"
    assert usuario_buscado.senha_hash == "hash_teste"
    assert usuario_buscado.papel == PapelUsuario.FUNCIONARIO
    assert usuario_buscado.ativo is True



def test_atualizar_usuario(repository):
    usuario = Usuario(
        nome="TESTE_USUARIO",
        senha_hash="hash_teste",
        papel=PapelUsuario.FUNCIONARIO
    )

    usuario = repository.criar(usuario)

    usuario.nome = "TESTE_USUARIO_ATUALIZADO"
    usuario.papel = PapelUsuario.GERENTE
    usuario.ativo = False

    repository.atualizar(usuario)

    usuario_atualizado = repository.buscar_por_id(
        usuario.id_usuario
    )

    assert usuario_atualizado.nome == "TESTE_USUARIO_ATUALIZADO"
    assert usuario_atualizado.papel == PapelUsuario.GERENTE
    assert usuario_atualizado.ativo is False

def test_buscar_usuario_inexistente(repository):
    usuario = repository.buscar_por_id(999999)

    assert usuario is None