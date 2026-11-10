from http import HTTPStatus

from src.enums import PapelEnum


def test_cadastrar_usuario_api(client_api, token_admin):
    cadastro = {'nome': 'Bob', 'senha': 'senha'}

    response = client_api.post(
        '/usuarios/cadastro',
        json=cadastro,
        headers={'Authorization': f'Bearer {token_admin}'},
    )
    assert response.status_code == HTTPStatus.CREATED

    dados = response.json()

    assert dados['id'] is not None
    assert dados['nome'] == 'Bob'
    assert dados['papel'] == PapelEnum.FUNCIONARIO.value
    assert dados['ativo'] is True


def test_cadastrar_usuario_retorna_403_se_service_retornar_permission_error(
    client_api, mock_usuario_service_api, token_funcionario
):
    mock_usuario_service_api.cadastrar_usuario.side_effect = PermissionError(
        'funcionários não tem permissão para cadastrar usuários'
    )
    response = client_api.post(
        '/usuarios/cadastro',
        json={'nome': 'Bob', 'senha': 'senha'},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'funcionários não tem permissão para cadastrar usuários'
    }


def test_listar_usuarios_retorna_lista_api(client_api, funcionario, token_admin):

    response = client_api.get(
        '/usuarios/listar', headers={'Authorization': f'Bearer {token_admin}'}
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json()['usuarios'][1] == {
        'id': funcionario.id,
        'nome': funcionario.nome,
        'ativo': funcionario.ativo,
        'papel': funcionario.papel,
    }


def test_funcionario_listar_usuarios_retorna_403(
    client_api, token_funcionario, mock_usuario_service_api
):
    mock_usuario_service_api.listar_usuarios.side_effect = PermissionError(
        'Funcionarios não tem permissão para listar funcionarios'
    )

    response = client_api.get(
        '/usuarios/listar', headers={'Authorization': f'Bearer {token_funcionario}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    assert response.json() == {
        'detail': 'Funcionarios não tem permissão para listar funcionarios'
    }


def test_atualizar_propria_senha_api(client_api, funcionario, token_funcionario):
    response = client_api.patch(
        '/usuarios/atualizar-senha',
        json={'senha_atual': funcionario.senha_limpa, 'nova_senha': 'nova-senha'},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'mensagem': 'Senha atualizada com sucesso.'}


def test_atualizar_senha_retorna_400_se_service_retornar_value_error(
    client_api, mock_usuario_service_api, token_funcionario
):
    mock_usuario_service_api.atualizar_senha_usuario.side_effect = ValueError(
        'A nova senha nao pode ser igual a atual.'
    )

    response = client_api.patch(
        '/usuarios/atualizar-senha',
        json={
            'senha_atual': 'senha-atual',
            'nova_senha': 'nova-atual',
        },
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'A nova senha nao pode ser igual a atual.'}


# Caso ocorra algo no meio do processo e o usuario nao exista mais no banco de dados
def test_atualizar_senha_retorna_404_se_service_retornar_lookup_error(
    client_api, mock_usuario_service_api, token_funcionario
):
    mock_usuario_service_api.atualizar_senha_usuario.side_effect = LookupError(
        'Usuario nao encontrado.'
    )
    response = client_api.patch(
        '/usuarios/atualizar-senha',
        json={
            'senha_atual': 'senha-atual',
            'nova_senha': 'nova_senha',
        },
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuario nao encontrado.'}


def test_atualizar_senha_retorna_403_se_service_retornar_permission_error(
    client_api, mock_usuario_service_api, token_funcionario
):
    mock_usuario_service_api.atualizar_senha_usuario.side_effect = PermissionError(
        'Usuario inativo.'
    )
    response = client_api.patch(
        '/usuarios/atualizar-senha',
        json={
            'senha_atual': 'senha-atual',
            'nova_senha': 'nova_senha',
        },
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Usuario inativo.'}
