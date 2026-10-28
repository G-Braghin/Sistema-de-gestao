from src.enums import PapelEnum
from tests.usuarios.conftest import UserFactory


def test_criar_e_buscar_usuario(user_repository):
    usuario = UserFactory.create(nome='test', senha='senha')
    usuario_criado = user_repository.criar(usuario)

    assert usuario_criado.id is not None

    usuario_buscado = user_repository.buscar_por_id(usuario_criado.id)

    assert usuario_buscado.id == usuario_criado.id
    assert usuario_buscado is not None
    assert usuario_buscado.nome == 'test'
    assert usuario_buscado.senha == 'senha'
    assert usuario_buscado.papel == usuario.papel
    assert usuario_buscado.ativo is True


def test_atualizar_usuario(user_repository):
    usuario = UserFactory.create()
    usuario = user_repository.criar(usuario)
    novos_dados = {
        'nome': 'nome atualizado',
        'papel': PapelEnum.GERENTE,
        'ativo': False,
    }
    user_repository.atualizar(usuario.id, novos_dados)
    usuario_atualizado = user_repository.buscar_por_id(usuario.id)
    assert usuario_atualizado.nome == 'nome atualizado'
    assert usuario_atualizado.papel == PapelEnum.GERENTE
    assert usuario_atualizado.ativo is False


def test_atualizar_usuario_nao_existe(user_repository):
    novos_dados = {
        'nome': 'nome atualizado',
        'papel': PapelEnum.GERENTE,
        'ativo': False,
    }

    response = user_repository.atualizar(user_id=999999, novos_dados=novos_dados)
    assert response is None


def test_buscar_usuario_inexistente(user_repository):
    usuario = user_repository.buscar_por_id(999999)
    assert usuario is None


def test_listar_usuarios_ativos(user_repository, session):
    user_ativo = UserFactory.create(ativo=True)
    user_inativo = UserFactory.create(ativo=False)
    session.add_all([user_ativo, user_inativo])
    session.flush()

    result = user_repository.listar()

    assert len(result) == 1
    assert result[0].nome == user_ativo.nome
    assert result[0].ativo


def test_listar_usuarios_desativados(user_repository, session):
    user_ativo = UserFactory.create(ativo=True)
    user_inativo = UserFactory.create(ativo=False)

    session.add_all([user_ativo, user_inativo])
    session.flush()

    result = user_repository.listar(False)

    assert len(result) == 1
    assert result[0].nome == user_inativo.nome
    assert not result[0].ativo


def test_usuario_nao_existe(user_repository):
    response = user_repository.existe_usuario()
    assert not response


def test_usuario_existe(user_repository, session):
    user = UserFactory.create()
    session.add(user)
    session.flush()

    response = user_repository.existe_usuario()
    assert response
