import pytest

from tests.usuarios.conftest import usuario_criar


def test_gerar_e_verificar_senha(user_auth):
    senha_hash = user_auth.gerar_senha_hash('senha-segura')

    assert senha_hash != 'senha-segura'
    assert user_auth.verificar_senha('senha-segura', senha_hash)
    assert not user_auth.verificar_senha('senha-incorreta', senha_hash)


def test_autenticar_usuario_ativo(user_auth, usuario):
    autenticado = user_auth.autenticar(usuario.id, usuario.senha_limpa)

    assert autenticado is usuario


@pytest.mark.parametrize(
    ('usuario_existe', 'senha'),
    [
        (False, 'senha-atual'),
        (True, 'senha-incorreta'),
    ],
)
def test_autenticar_rejeita_credenciais_invalidas(
    user_auth, usuario, usuario_existe, senha
):
    id_usuario = usuario.id if usuario_existe else usuario.id + 999

    with pytest.raises(ValueError, match='ID ou Senha Invalidos'):
        user_auth.autenticar(id_usuario, senha)


def test_nao_autenticar_usuario_inativo(user_auth, session):
    usuario = usuario_criar(session, user_auth, ativo=False)

    with pytest.raises(ValueError, match='Usuário inativo'):
        user_auth.autenticar(usuario.id, usuario.senha_limpa)


@pytest.mark.parametrize(
    ('id_usuario', 'tipo_erro', 'mensagem'),
    [
        (0, ValueError, 'ID de usuario invalido'),
        (-1, ValueError, 'ID de usuario invalido'),
        ('abc', TypeError, 'ID tem que ser um numero inteiro'),
        (True, TypeError, 'ID tem que ser um numero inteiro'),
    ],
)
def test_autenticar_rejeita_id_invalido(user_auth, id_usuario, tipo_erro, mensagem):
    with pytest.raises(tipo_erro, match=mensagem):
        user_auth.autenticar(id_usuario, 'senha-atual')


@pytest.mark.parametrize('senha', ['', '   ', None])
def test_autenticar_rejeita_senha_vazia(user_auth, senha):
    with pytest.raises(ValueError, match='Senha nao pode estar vazio'):
        user_auth.autenticar(1, senha)


def test_atualizar_senha_usuario(user_auth, usuario):
    resultado = user_auth.atualizar_senha_usuario(
        usuario.id, usuario.senha_limpa, nova_senha='senha-nova'
    )

    assert resultado.id is usuario.id
    assert user_auth.verificar_senha('senha-nova', resultado.senha)
    assert not user_auth.verificar_senha('senha-atual', resultado.senha)


def test_atualizar_senha_rejeita_senha_atual_incorreta(user_auth, session):
    usuario = usuario_criar(session, user_auth)

    with pytest.raises(ValueError, match='Senha atual incorreta'):
        user_auth.atualizar_senha_usuario(usuario.id, 'senha-incorreta', 'senha-nova')


def test_atualizar_senha_rejeita_usuario_inexistente(user_auth):

    with pytest.raises(ValueError, match='Usuário não encontrado'):
        user_auth.atualizar_senha_usuario(999999, 'senha-atual', 'senha-nova')


@pytest.mark.parametrize(
    ('id_usuario', 'tipo_erro', 'mensagem'),
    [
        (0, ValueError, 'ID de usuario invalido'),
        (-1, ValueError, 'ID de usuario invalido'),
        ('abc', TypeError, 'ID tem que ser um numero inteiro'),
        (True, TypeError, 'ID tem que ser um numero inteiro'),
    ],
)
def test_atualizar_senha_rejeita_id_invalido(
    user_auth, id_usuario, tipo_erro, mensagem
):
    with pytest.raises(tipo_erro, match=mensagem):
        user_auth.atualizar_senha_usuario(id_usuario, 'senha-atual', 'senha-nova')


@pytest.mark.parametrize(
    ('senha_atual', 'nova_senha', 'mensagem'),
    [
        ('', 'senha-nova', 'A senha atual nao pode estar vazio'),
        ('   ', 'senha-nova', 'A senha atual nao pode estar vazio'),
        (None, 'senha-nova', 'A senha atual nao pode estar vazio'),
        ('senha-atual', '', 'A nova senha nao pode estar vazio'),
        ('senha-atual', '   ', 'A nova senha nao pode estar vazio'),
        ('senha-atual', None, 'A nova senha nao pode estar vazio'),
    ],
)
def test_atualizar_senha_rejeita_senhas_vazias(
    user_auth, senha_atual, nova_senha, mensagem
):
    with pytest.raises(ValueError, match=mensagem):
        user_auth.atualizar_senha_usuario(1, senha_atual, nova_senha)


def test_atualizar_senha_rejeita_nova_senha_igual_a_atual(user_auth, usuario):
    senha_hash_original = usuario.senha

    with pytest.raises(ValueError, match='A nova senha nao pode ser igual a atual'):
        user_auth.atualizar_senha_usuario(usuario.id, 'senha-atual', 'senha-atual')
    assert usuario.senha == senha_hash_original
