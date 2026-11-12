from http import HTTPStatus

import pytest


def test_cadastrar_cliente_api(client_api, token_funcionario):
    response = client_api.post(
        '/clientes/cadastro',
        json={
            'nome': 'Bob',
            'cpf': '860.795.260-93',
            'telefone': '67999551122',
            'endereco': 'Rua A',
        },
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['id'] is not None
    assert response.json()['cpf'] == '860.***.***-93'
    assert response.json()['telefone'] == '(67) 99955-1122'
    assert response.json()['endereco'] == 'Rua A'
    assert response.json()['ativo'] is True


def test_buscar_cliente_cpf_api(client_api, token_funcionario, cliente_db):

    response = client_api.post(
        '/clientes/buscar',
        json={'cpf': cliente_db.cpf},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['id'] == cliente_db.id
    assert response.json()['nome'] == cliente_db.nome
    assert response.json()['endereco'] == cliente_db.endereco


def test_atualizar_cliente_api(client_api, token_funcionario, cliente_db):
    cpf_mascarado = f'{cliente_db.cpf[:3]}.***.***-{cliente_db.cpf[9:]}'
    response = client_api.patch(
        f'/clientes/{cliente_db.id}/atualizar-info',
        json={'nome': 'Bob', 'telefone': '67999668855', 'endereco': 'Rua B'},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': cliente_db.id,
        'nome': 'Bob',
        'cpf': cpf_mascarado,
        'telefone': '(67) 99966-8855',
        'ativo': True,
        'endereco': 'Rua B',
    }


def test_atualizar_so_um_campo_cliente_api(client_api, token_funcionario, cliente_db):
    cpf_mascarado = f'{cliente_db.cpf[:3]}.***.***-{cliente_db.cpf[9:]}'
    response = client_api.patch(
        f'/clientes/{cliente_db.id}/atualizar-info',
        json={'telefone': '67999668855'},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': cliente_db.id,
        'nome': cliente_db.nome,
        'cpf': cpf_mascarado,
        'telefone': '(67) 99966-8855',
        'ativo': True,
        'endereco': cliente_db.endereco,
    }


@pytest.mark.parametrize('status', [True, False])
def test_mudar_status_cliente_api(client_api, token_admin, cliente_db, session, status):
    cliente_db.ativo = False if status else True
    session.add(cliente_db)
    session.commit()
    session.refresh(cliente_db)

    status_mensagem = 'ativado' if status else 'desativado'

    response = client_api.patch(
        f'/clientes/{cliente_db.id}/status',
        json={'ativo': status},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'mensagem': f'Cliente {cliente_db.nome} {status_mensagem} com sucesso.'
    }


def test_listar_clientes_api(client_api, token_admin, cliente_db):
    cpf_mascarado = f'{cliente_db.cpf[:3]}.***.***-{cliente_db.cpf[9:]}'
    telefone_formatado = (
        f'({cliente_db.telefone[:2]}) '
        f'{cliente_db.telefone[2:7]}-{cliente_db.telefone[7:]}'
    )
    response = client_api.get(
        '/clientes/listar',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['clientes'] == [
        {
            'id': cliente_db.id,
            'nome': cliente_db.nome,
            'telefone': telefone_formatado,
            'cpf': cpf_mascarado,
            'ativo': True,
        }
    ]


def test_cadastrar_cliente_retorna_400_se_service_retornar_value_error(
    client_api,
    token_funcionario,
    mock_cliente_service_api,
):
    mock_cliente_service_api.cadastrar_cliente.side_effect = ValueError(
        'CPF ja existe no sistema.'
    )

    response = client_api.post(
        '/clientes/cadastro',
        json={
            'nome': 'Bob',
            'cpf': '860.795.260-93',
            'telefone': '67999551122',
            'endereco': 'Rua A',
        },
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'CPF ja existe no sistema.'}


def test_buscar_cliente_retorna_400_se_service_retornar_value_error(
    client_api, token_funcionario, mock_cliente_service_api
):

    mock_cliente_service_api.buscar_cliente_cpf.side_effect = ValueError(
        'Cliente inativo.'
    )

    response = client_api.post(
        '/clientes/buscar',
        json={'cpf': '860.795.260-93'},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Cliente inativo.'}


def test_buscar_cliente_retorna_404_se_service_retornar_lookup_error(
    client_api, token_funcionario, mock_cliente_service_api
):
    mock_cliente_service_api.buscar_cliente_cpf.side_effect = LookupError(
        'Cliente nao encontrado'
    )

    response = client_api.post(
        '/clientes/buscar',
        json={'cpf': '860.795.260-93'},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Cliente nao encontrado'}


def test_atualizar_cliente_retorna_400_se_service_retornar_value_error(
    client_api, token_funcionario, mock_cliente_service_api
):
    mock_cliente_service_api.atualizar.side_effect = ValueError('Cliente inativo.')

    response = client_api.patch(
        '/clientes/10/atualizar-info',
        json={'nome': 'novo-nome'},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Cliente inativo.'}


def test_atualizar_cliente_retorna_404_se_service_retornar_lookup_error(
    client_api, token_funcionario, mock_cliente_service_api
):
    mock_cliente_service_api.atualizar.side_effect = LookupError(
        'Cliente nao encontrado'
    )

    response = client_api.patch(
        '/clientes/10/atualizar-info',
        json={'nome': 'novo-nome'},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Cliente nao encontrado'}


def test_mudar_status_cliente_retorna_400_se_service_retornar_value_error(
    client_api, token_admin, mock_cliente_service_api
):
    mock_cliente_service_api.atualizar_status.side_effect = ValueError(
        'Cliente ja ativado.'
    )

    response = client_api.patch(
        '/clientes/10/status',
        json={'ativo': True},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Cliente ja ativado.'}


def test_mudar_status_cliente_retorna_404_se_service_retornar_lookup_error(
    client_api, token_admin, mock_cliente_service_api
):
    mock_cliente_service_api.atualizar_status.side_effect = LookupError(
        'Cliente nao encontrado.'
    )

    response = client_api.patch(
        '/clientes/10/status',
        json={'ativo': False},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Cliente nao encontrado.'}


def test_mudar_status_cliente_retorna_403_se_service_retornar_permission_error(
    client_api, token_funcionario, mock_cliente_service_api
):
    mock_cliente_service_api.atualizar_status.side_effect = PermissionError(
        'Sem permissao.'
    )

    response = client_api.patch(
        '/clientes/10/status',
        json={'ativo': False},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissao.'}


def test_listar_clientes_retorna_403_se_service_retornar_permission_error(
    client_api, token_funcionario, mock_cliente_service_api
):
    mock_cliente_service_api.listar.side_effect = PermissionError('Sem permissao.')

    response = client_api.get(
        '/clientes/listar',
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissao.'}
