import pytest

from src.database.conexao import Conexao
from src.entities.usuario import Usuario
from src.entities.dtos.usuario_resumo import UsuarioResumo
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


def test_listar_usuarios_ativos(repository):
    ativo = repository.criar(Usuario(
        nome="TESTE_USUARIO_ATIVO",
        senha_hash="hash_teste",
        papel=PapelUsuario.FUNCIONARIO,
        ativo=True
    ))
    desativado = repository.criar(Usuario(
        nome="TESTE_USUARIO_DESATIVADO",
        senha_hash="hash_teste",
        papel=PapelUsuario.GERENTE,
        ativo=False
    ))

    usuarios = repository.listar()
    ids = [usuario.id_usuario for usuario in usuarios]

    assert ativo.id_usuario in ids
    assert desativado.id_usuario not in ids
    assert all(usuario.ativo is True for usuario in usuarios)
    assert all(isinstance(usuario, UsuarioResumo) for usuario in usuarios)
    assert all(not hasattr(usuario, "senha_hash") for usuario in usuarios)

    resumo = next(
        usuario for usuario in usuarios
        if usuario.id_usuario == ativo.id_usuario
    )
    assert resumo.nome == ativo.nome
    assert resumo.papel == ativo.papel


def test_listar_usuarios_desativados(repository):
    ativo = repository.criar(Usuario(
        nome="TESTE_USUARIO_ATIVO",
        senha_hash="hash_teste",
        papel=PapelUsuario.FUNCIONARIO,
        ativo=True
    ))
    desativado = repository.criar(Usuario(
        nome="TESTE_USUARIO_DESATIVADO",
        senha_hash="hash_teste",
        papel=PapelUsuario.GERENTE,
        ativo=False
    ))

    usuarios = repository.listar(False)
    ids = [usuario.id_usuario for usuario in usuarios]

    assert desativado.id_usuario in ids
    assert ativo.id_usuario not in ids
    assert all(usuario.ativo is False for usuario in usuarios)
    assert all(isinstance(usuario, UsuarioResumo) for usuario in usuarios)
    assert all(not hasattr(usuario, "senha_hash") for usuario in usuarios)

    resumo = next(
        usuario for usuario in usuarios
        if usuario.id_usuario == desativado.id_usuario
    )
    assert resumo.nome == desativado.nome
    assert resumo.papel == desativado.papel


def test_listar_usuarios_ordenados_por_papel_e_nome(repository):
    usuarios_criados = []
    for papel in (
        PapelUsuario.FUNCIONARIO,
        PapelUsuario.GERENTE,
        PapelUsuario.ADMINISTRADOR
    ):
        for nome in ("TESTE_ZULU", "TESTE_ALFA"):
            usuario = repository.criar(Usuario(
                nome=nome,
                senha_hash="hash_teste",
                papel=papel,
                ativo=True
            ))
            usuarios_criados.append(usuario)

    ids_criados = [usuario.id_usuario for usuario in usuarios_criados]
    usuarios = repository.listar()
    resultado = [
        (usuario.papel, usuario.nome)
        for usuario in usuarios
        if usuario.id_usuario in ids_criados
    ]

    assert resultado == [
        (PapelUsuario.ADMINISTRADOR, "TESTE_ALFA"),
        (PapelUsuario.ADMINISTRADOR, "TESTE_ZULU"),
        (PapelUsuario.GERENTE, "TESTE_ALFA"),
        (PapelUsuario.GERENTE, "TESTE_ZULU"),
        (PapelUsuario.FUNCIONARIO, "TESTE_ALFA"),
        (PapelUsuario.FUNCIONARIO, "TESTE_ZULU")
    ]
