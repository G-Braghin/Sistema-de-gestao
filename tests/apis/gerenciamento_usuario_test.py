from http import HTTPStatus


def test_promover_gerente_a_gerente_api(client_api, funcionario, token_admin):
    response = client_api.patch(
        f'usuarios/{funcionario.id}/promover',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {
        'mensagem': f'{funcionario.nome} foi promovido com sucesso.'
    }


def test_promover_retorna_400_se_service_retornar_value_error(
    client_api, mock_usuario_service_api, token_admin
):
    mock_usuario_service_api.promover_a_gerente.side_effect = ValueError(
        'ID de usuário invalido.'
    )

    response = client_api.patch(
        'usuarios/-1/promover',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'ID de usuário invalido.'}


def test_promover_retorna_404_se_service_retornar_lookup_error(
    client_api, mock_usuario_service_api, token_admin
):
    mock_usuario_service_api.promover_a_gerente.side_effect = LookupError(
        'Usuario nao encontrado.'
    )
    response = client_api.patch(
        'usuarios/9999999/promover',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuario nao encontrado.'}


def test_promover_retorna_403_se_service_retornar_permission_error(
    client_api, mock_usuario_service_api, token_funcionario
):
    mock_usuario_service_api.promover_a_gerente.side_effect = PermissionError(
        'Sem permissao para promover.'
    )
    response = client_api.patch(
        'usuarios/1/promover',
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissao para promover.'}


def test_atualizar_status_usuario_ativo_para_inativo_api(
    client_api, token_admin, funcionario
):
    response = client_api.patch(
        f'usuarios/{funcionario.id}/atualizar-status',
        json={'ativo': False},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'mensagem': f'Usuario {funcionario.nome} desativado com sucesso.'
    }


def test_atualizar_status_usuario_inativo_para_ativo_api(
    client_api, token_admin, funcionario_inativo
):
    response = client_api.patch(
        f'usuarios/{funcionario_inativo.id}/atualizar-status',
        json={'ativo': True},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'mensagem': f'Usuario {funcionario_inativo.nome} ativado com sucesso.'
    }


def test_atualizar_status_retorna_400_se_service_retornar_value_error(
    client_api, mock_usuario_service_api, token_admin
):
    mock_usuario_service_api.atualizar_status.side_effect = ValueError(
        'Usuario ja esta ativo.'
    )
    response = client_api.patch(
        'usuarios/1/atualizar-status',
        json={'ativo': True},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Usuario ja esta ativo.'}


def test_atualizar_status_retorna_404_se_service_retornar_lookup_eroor(
    client_api, mock_usuario_service_api, token_admin
):
    mock_usuario_service_api.atualizar_status.side_effect = LookupError(
        'Usuario nao encontrado.'
    )
    response = client_api.patch(
        'usuarios/1/atualizar-status',
        json={'ativo': True},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuario nao encontrado.'}


def test_atualizar_status_retorna_403_se_service_retornar_permission_error(
    client_api, mock_usuario_service_api, token_funcionario
):
    mock_usuario_service_api.atualizar_status.side_effect = PermissionError(
        'Sem permissao para atualizar'
    )
    response = client_api.patch(
        'usuarios/1/atualizar-status',
        json={'ativo': True},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissao para atualizar'}


def test_resetar_senha_de_funcionario_api(client_api, funcionario, token_admin):

    response = client_api.patch(
        f'/usuarios/{funcionario.id}/resetar-senha',
        json={'nova_senha': 'nova_senha'},
        headers={'Authorization': f'Bearer {token_admin}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'mensagem': f'Senha de {funcionario.nome} redefinida com sucesso.'
    }


def test_resetar_senha_retorna_400_se_service_retornar_value_error(
    client_api, mock_usuario_service_api, token_admin
):
    mock_usuario_service_api.resetar_senha.side_effect = ValueError('ID invalido.')
    response = client_api.patch(
        '/usuarios/-1/resetar-senha',
        json={'nova_senha': 'nova_senha'},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'ID invalido.'}


def test_resetar_senha_retorna_404_se_service_retornar_lookup_error(
    client_api, mock_usuario_service_api, token_admin
):
    mock_usuario_service_api.resetar_senha.side_effect = LookupError(
        'ID nao encontrado.'
    )
    response = client_api.patch(
        '/usuarios/999999/resetar-senha',
        json={'nova_senha': 'nova_senha'},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'ID nao encontrado.'}


def test_resetar_senha_retorna_403_se_service_retornar_permission_error(
    client_api, mock_usuario_service_api, token_funcionario
):
    mock_usuario_service_api.resetar_senha.side_effect = PermissionError(
        'Sem permissao para resetar senha.'
    )
    response = client_api.patch(
        '/usuarios/1/resetar-senha',
        json={'nova_senha': 'nova_senha'},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissao para resetar senha.'}
