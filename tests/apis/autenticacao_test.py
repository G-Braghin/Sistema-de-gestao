from http import HTTPStatus


def test_fazer_login_com_sucesso(client_api, funcionario):

    response = client_api.post(
        '/autenticacao/login',
        data={'username': funcionario.id, 'password': funcionario.senha_limpa},
    )

    assert response.status_code == HTTPStatus.OK
    token = response.json()
    assert 'access_token' in token
    assert token['token_type'] == 'Bearer'


def test_login_retorna_401_com_id_invalido(client_api):
    response = client_api.post(
        '/autenticacao/login',
        data={'username': 'abc', 'password': 'senha'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Credenciais inválidas.'


def test_login_retorna_401_se_service_retorna_value_error(
    client_api, mock_auth_service
):
    mock_auth_service.autenticar.side_effect = ValueError('ID ou Senha Invalidos.')
    response = client_api.post(
        '/autenticacao/login',
        data={'username': '-1', 'password': 'senha'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'ID ou Senha Invalidos.'


def test_login_retorna_403_se_service_retornar_permission_error(
    client_api, mock_auth_service
):
    mock_auth_service.autenticar.side_effect = PermissionError('Usuário inativo.')

    response = client_api.post(
        '/autenticacao/login',
        data={'username': '1', 'password': 'senha'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()['detail'] == 'Usuário inativo.'
