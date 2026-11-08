from http import HTTPStatus


def test_fazer_login_com_sucesso(api_client, mock_auth_service, user_funcionario):
    mock_auth_service.autenticar.return_value = user_funcionario
    user_funcionario.senha = 'test'
    response = api_client.post(
        '/autenticacao/login',
        data={'username': user_funcionario.id, 'password': 'test'},
    )

    assert response.status_code == HTTPStatus.OK
    token = response.json()
    assert 'access_token' in token
    assert token['token_type'] == 'Bearer'


def test_login_retorna_401_caso_id_nao_senha_inteiro(api_client, mock_auth_service):
    mock_auth_service.autenticar.side_effect = ValueError('Credenciais inválidas.')

    response = api_client.post(
        '/autenticacao/login',
        data={'username': 'abc', 'password': 'senha'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Credenciais inválidas.'


def test_login_rotorna_401_com_credenciais_invalidas(api_client, mock_auth_service):
    mock_auth_service.autenticar.side_effect = ValueError('ID ou Senha Invalidos.')

    response = api_client.post(
        '/autenticacao/login',
        data={'username': '1', 'password': 'senha-errada'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'ID ou Senha Invalidos.'


def test_login_retorna_403_com_usuario_inativo(api_client, mock_auth_service):
    mock_auth_service.autenticar.side_effect = PermissionError('Usuário inativo.')

    response = api_client.post(
        '/autenticacao/login',
        data={'username': '10', 'password': 'test'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()['detail'] == 'Usuário inativo.'
