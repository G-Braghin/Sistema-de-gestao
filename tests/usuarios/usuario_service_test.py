import pytest

from src.enums import PapelEnum
from tests.usuarios.conftest import UserFactory


def criar_usuario_com_id(id, **kwargs):
    usuario = UserFactory.create(**kwargs)
    usuario.id = id
    return usuario


@pytest.mark.parametrize(
    ('papel_logado', 'papel_alvo', 'pode_gerenciar'),
    [
        (PapelEnum.ADMIN, PapelEnum.ADMIN, True),
        (PapelEnum.ADMIN, PapelEnum.GERENTE, True),
        (PapelEnum.ADMIN, PapelEnum.FUNCIONARIO, True),
        (PapelEnum.GERENTE, PapelEnum.FUNCIONARIO, True),
        (PapelEnum.GERENTE, PapelEnum.ADMIN, False),
        (PapelEnum.GERENTE, PapelEnum.GERENTE, False),
        (PapelEnum.FUNCIONARIO, PapelEnum.FUNCIONARIO, False),
    ],
)
def test_pode_gerenciar_por_papel(
    user_service, papel_logado, papel_alvo, pode_gerenciar
):
    usuario_logado = UserFactory.create(papel=papel_logado)
    usuario_alvo = UserFactory.create(papel=papel_alvo)

    assert user_service.pode_gerenciar(usuario_logado, usuario_alvo) is pode_gerenciar


@pytest.mark.parametrize(
    ('papel_logado', 'papel_cadastrado'),
    [
        (PapelEnum.ADMIN, PapelEnum.FUNCIONARIO),
        (PapelEnum.ADMIN, PapelEnum.GERENTE),
        (PapelEnum.GERENTE, PapelEnum.FUNCIONARIO),
    ],
)
def test_cadastrar_usuario_com_permissao(
    user_service, user_repository_mock, user_auth_mock, papel_logado, papel_cadastrado
):
    responsavel = UserFactory.create(papel=papel_logado)
    cadastrado = criar_usuario_com_id(999, papel=papel_cadastrado, nome='Joao')
    user_repository_mock.criar.return_value = cadastrado
    user_auth_mock.verificar_senha.return_value = True

    response = user_service.cadastrar_usuario(responsavel, cadastrado)

    assert response.id is not None
    assert response.nome == 'Joao'
    assert response.papel == papel_cadastrado


def test_cadastrar_usuario_sem_cargo_permitido(user_service):
    gerente = UserFactory.create(papel=PapelEnum.GERENTE)
    cadastrado = UserFactory.create(papel=PapelEnum.GERENTE)
    with pytest.raises(PermissionError, match='Você não pode cadastrar esse cargo'):
        user_service.cadastrar_usuario(gerente, cadastrado)


def test_admin_promove_funcionario_a_gerente(user_service, user_repository_mock):
    admin = UserFactory.create(papel=PapelEnum.ADMIN)
    funcionario = criar_usuario_com_id(
        999, nome='Funcionario', papel=PapelEnum.FUNCIONARIO
    )
    funcionario_atualizado = criar_usuario_com_id(
        999, nome='Funcionario', papel=PapelEnum.GERENTE
    )
    user_repository_mock.buscar_por_id.return_value = funcionario
    user_repository_mock.atualizar.return_value = funcionario_atualizado

    resultado = user_service.promover_a_gerente(admin, funcionario.id)

    assert resultado.id == funcionario.id
    assert resultado.papel == PapelEnum.GERENTE


def test_gerente_nao_pode_promover_funcionario(user_service):
    gerente = UserFactory.create(papel=PapelEnum.GERENTE)
    funcionario = criar_usuario_com_id(
        999, nome='Funcionario', papel=PapelEnum.FUNCIONARIO
    )

    with pytest.raises(PermissionError, match='Apenas administradores'):
        user_service.promover_a_gerente(gerente, funcionario.id)

    assert funcionario.papel == PapelEnum.FUNCIONARIO


@pytest.mark.parametrize('papel_alvo', [PapelEnum.GERENTE, PapelEnum.ADMIN])
def test_apenas_funcionario_pode_ser_promovido(user_service, session, papel_alvo):
    admin = UserFactory.create(papel=PapelEnum.ADMIN)
    usuario = criar_usuario_com_id(999, papel=papel_alvo)

    with pytest.raises(ValueError, match='Apenas funcionários'):
        user_service.promover_a_gerente(admin, usuario.id)


@pytest.mark.parametrize(
    ('id_usuario', 'tipo_erro', 'mensagem'),
    [
        (0, ValueError, 'ID de usuário invalido'),
        (-1, ValueError, 'ID de usuário invalido'),
        ('abc', TypeError, 'ID tem que ser um numero inteiro'),
        (True, TypeError, 'ID tem que ser um numero inteiro'),
    ],
)
@pytest.mark.parametrize(
    'operacao',
    ['promover_a_gerente', 'resetar_senha', 'atualizar_status'],
)
def test_operacoes_rejeitam_ids_invalidos(
    user_service, id_usuario, tipo_erro, mensagem, operacao
):
    admin = UserFactory.create(papel=PapelEnum.ADMIN)
    chamada = {
        'promover_a_gerente': lambda: user_service.promover_a_gerente(
            admin, id_usuario
        ),
        'resetar_senha': lambda: user_service.resetar_senha(
            admin, id_usuario, 'nova-senha'
        ),
        'atualizar_status': lambda: user_service.atualizar_status(
            admin, id_usuario, False
        ),
    }

    with pytest.raises(tipo_erro, match=mensagem):
        chamada[operacao]()


def test_resetar_senha_de_funcionario(
    user_service, user_auth_mock, user_repository_mock
):
    gerente = UserFactory.create(papel=PapelEnum.GERENTE)
    funcionario = criar_usuario_com_id(
        999, nome='Funcionario', papel=PapelEnum.FUNCIONARIO
    )

    user_repository_mock.buscar_por_id.return_value = funcionario
    user_repository_mock.atualizar.return_value = funcionario
    hash_fake = 'novo-hash-criptografado-fake'
    user_auth_mock.gerar_senha_hash.return_value = hash_fake

    resultado = user_service.resetar_senha(gerente, funcionario.id, 'nova-senha')

    assert resultado.id == funcionario.id
    user_auth_mock.gerar_senha_hash.assert_called_once_with('nova-senha')
    user_repository_mock.atualizar.assert_called_once_with(
        funcionario.id, {'senha': hash_fake}
    )


def test_gerente_nao_pode_resetar_senha_de_gerente(
    user_service,
):
    gerente = UserFactory.create(papel=PapelEnum.GERENTE)
    outro_gerente = criar_usuario_com_id(999, papel=PapelEnum.GERENTE)
    senha_original = outro_gerente.senha

    with pytest.raises(PermissionError, match='Você não tem permissão'):
        user_service.resetar_senha(gerente, outro_gerente.id, 'nova-senha')

    assert outro_gerente.senha == senha_original


@pytest.mark.parametrize(
    'nova_senha',
    ['', '   ', None],
)
def test_resetar_senha_rejeita_senha_vazia(user_service, nova_senha):
    admin = UserFactory.create(papel=PapelEnum.ADMIN)
    funcionario = criar_usuario_com_id(999, papel=PapelEnum.FUNCIONARIO)
    senha_original = funcionario.senha

    with pytest.raises(ValueError, match='Senha não pode estar vazio'):
        user_service.resetar_senha(admin, funcionario.id, nova_senha)

    assert funcionario.senha == senha_original


@pytest.mark.parametrize(
    'caso',
    [
        (PapelEnum.GERENTE, PapelEnum.FUNCIONARIO, True, False),
        (PapelEnum.GERENTE, PapelEnum.FUNCIONARIO, False, True),
        (PapelEnum.ADMIN, PapelEnum.FUNCIONARIO, True, False),
        (PapelEnum.ADMIN, PapelEnum.GERENTE, False, True),
    ],
)
def test_atualizar_status_com_permissao(user_service, user_repository_mock, caso):
    papel_responsavel, papel_alvo, ativo_inicial, ativo_final = caso
    responsavel = UserFactory.create(papel=papel_responsavel)
    usuario = criar_usuario_com_id(
        999, nome='Alvo', papel=papel_alvo, ativo=ativo_inicial
    )
    usuario_att = criar_usuario_com_id(
        999, nome='Alvo', papel=papel_alvo, ativo=ativo_final
    )
    user_repository_mock.buscar_por_id.return_value = usuario
    user_repository_mock.atualizar.return_value = usuario_att

    resultado = user_service.atualizar_status(responsavel, usuario.id, ativo_final)

    usuario_att.id = resultado.id
    assert resultado.ativo is ativo_final


def test_admin_nao_pode_alterar_status_de_outro_admin(
    user_service, user_repository_mock
):
    admin = UserFactory.create(papel=PapelEnum.ADMIN)
    outro_admin = criar_usuario_com_id(999, nome='Outro admin', papel=PapelEnum.ADMIN)
    user_repository_mock.buscar_por_id.return_value = outro_admin

    with pytest.raises(PermissionError, match='Contas de administradores'):
        user_service.atualizar_status(admin, outro_admin.id, False)

    assert outro_admin.ativo is True
    user_repository_mock.atualizar.assert_not_called()


def test_gerente_nao_pode_alterar_status_de_gerente(user_service):
    gerente = UserFactory.create(papel=PapelEnum.GERENTE)
    outro_gerente = criar_usuario_com_id(999, papel=PapelEnum.GERENTE)

    with pytest.raises(PermissionError, match='não tem permissão'):
        user_service.atualizar_status(gerente, outro_gerente.id, False)

    assert outro_gerente.ativo is True


def test_usuario_nao_pode_desativar_a_propria_conta(user_service, user_repository_mock):
    gerente = criar_usuario_com_id(999, nome='Gerente', papel=PapelEnum.GERENTE)
    user_repository_mock.buscar_por_id.return_value = gerente

    with pytest.raises(ValueError, match='desativar a própria conta'):
        user_service.atualizar_status(gerente, gerente.id, False)

    assert gerente.ativo is True
    user_repository_mock.atualizar.assert_not_called()


@pytest.mark.parametrize('status_ativo', ['False', None, 0, 1])
def test_atualizar_status_rejeita_valor_que_nao_seja_boolean(
    user_service, status_ativo
):
    admin = UserFactory.create(papel=PapelEnum.ADMIN)
    funcionario = criar_usuario_com_id(999, papel=PapelEnum.FUNCIONARIO)

    with pytest.raises(TypeError, match='Status deve ser True ou False'):
        user_service.atualizar_status(admin, funcionario.id, status_ativo)

    assert funcionario.ativo is True


@pytest.mark.parametrize(
    ('status_inicial', 'status_solicitado', 'mensagem'),
    [
        (True, True, 'Usuario ja esta ativo'),
        (False, False, 'Usuario ja esta desativado'),
    ],
)
def test_atualizar_status_rejeita_status_inalterado(
    user_service, user_repository_mock, status_inicial, status_solicitado, mensagem
):
    admin = UserFactory.create(papel=PapelEnum.ADMIN)
    funcionario = criar_usuario_com_id(
        999, papel=PapelEnum.FUNCIONARIO, ativo=status_solicitado
    )

    user_repository_mock.buscar_por_id.return_value = funcionario

    with pytest.raises(ValueError, match=mensagem):
        user_service.atualizar_status(admin, funcionario.id, status_solicitado)

    assert funcionario.ativo is status_inicial


@pytest.mark.parametrize(
    ('papel_responsavel', 'total_esperado'),
    [
        (PapelEnum.ADMIN, 3),
        (PapelEnum.GERENTE, 1),
    ],
)
def test_listar_usuarios_respeita_papel(
    user_service, user_repository_mock, papel_responsavel, total_esperado
):
    responsavel = UserFactory.create(papel=papel_responsavel)
    usuarios = [
        UserFactory.build(papel=PapelEnum.ADMIN),
        UserFactory.build(papel=PapelEnum.GERENTE),
        UserFactory.build(papel=PapelEnum.FUNCIONARIO),
    ]
    user_repository_mock.listar.return_value = usuarios

    resultado = user_service.listar_usuarios(responsavel)

    assert len(resultado) == total_esperado

    if papel_responsavel == PapelEnum.GERENTE:
        assert resultado[0].papel == PapelEnum.FUNCIONARIO


def test_funcionario_nao_pode_listar_usuarios(user_service):
    funcionario = UserFactory.create(papel=PapelEnum.FUNCIONARIO)

    with pytest.raises(PermissionError, match='não tem permissão para listar'):
        user_service.listar_usuarios(funcionario)


def test_criar_admin_padrao_quando_nao_existe_usuario(
    user_service, user_repository_mock
):
    admin = criar_usuario_com_id(999, senha='senha-admin-teste', papel=PapelEnum.ADMIN)
    user_repository_mock.criar.return_value = admin
    user_repository_mock.existe_usuario.return_value = False
    admin_criado = user_service.criar_admin_padrao()

    assert admin_criado is not None
    assert admin_criado.id is not None
    assert admin_criado.papel == PapelEnum.ADMIN


def test_nao_criar_admin_padrao_se_ja_existe_usuario(
    user_service, user_repository_mock
):
    user_repository_mock.existe_usuario.return_value = True
    assert user_service.criar_admin_padrao() is None
