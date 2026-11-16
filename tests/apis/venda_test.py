from datetime import timezone
from http import HTTPStatus
from zoneinfo import ZoneInfo

from src.enums import StatusVenda


def test_realizar_venda_api(client_api, token_admin, cliente_db, produto_db, admin):
    itens = [{'id_produto': produto_db.id, 'quantidade': 1}]

    response = client_api.post(
        f'/vendas/{cliente_db.id}/vender',
        json=itens,
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['id'] is not None
    assert response.json()['id_cliente'] == cliente_db.id
    assert response.json()['id_usuario'] == admin.id
    assert response.json()['status'] == StatusVenda.CONCLUIDA
    for item in response.json()['itens']:
        assert item['id'] is not None
        assert item['id_produto'] == produto_db.id
        assert item['quantidade'] == 1


def test_cancelar_venda_api(client_api, token_admin, venda):

    response = client_api.post(
        f'/vendas/{venda.id}/cancelar',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['status'] == StatusVenda.CANCELADA


def test_listar_resumo_venda_api(
    client_api, token_admin, venda, cliente_db, usuario_db
):
    hora_formatada = (
        venda.created_at
        .replace(tzinfo=timezone.utc)
        .astimezone(ZoneInfo('America/Sao_Paulo'))
        .strftime('%d/%m/%Y %H:%M')
    )
    valor_formatado = (
        f'R$ {venda.valor_total:,.2f}'
        .replace(',', 'X')
        .replace('.', ',')
        .replace('X', '.')
    )
    response = client_api.get(
        '/vendas/listar',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['vendas'] == [
        {
            'id_venda': venda.id,
            'nome_cliente': cliente_db.nome,
            'nome_vendedor': usuario_db.nome,
            'data_venda': hora_formatada,
            'valor_total': valor_formatado,
            'status': StatusVenda.CONCLUIDA.value,
        }
    ]


def test_listar_venda_detalhe_api(client_api, token_admin, venda):
    response = client_api.get(
        f'/vendas/{venda.id}/listar-detalhe',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['id'] == venda.id
    assert response.json()['id_cliente'] == venda.id_cliente
    assert response.json()['id_usuario'] == venda.id_usuario
    assert response.json()['status'] == venda.status
    for item in response.json()['itens']:
        for venda_item in venda.itens:
            assert item['id'] == venda_item.id
            assert item['id_produto'] == venda_item.id_produto
            assert item['quantidade'] == venda_item.quantidade


def test_realizar_venda_retorna_422_se_service_retornar_value_error(
    client_api, token_admin, mock_venda_service_api
):
    itens = [{'id_produto': 1, 'quantidade': 1}]
    mock_venda_service_api.realizar_venda.side_effect = ValueError(
        'Cliente desativado.'
    )

    response = client_api.post(
        '/vendas/10/vender',
        json=itens,
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == {'detail': 'Cliente desativado.'}


def test_realizar_venda_retorna_404_se_service_retornar_lookup_error(
    client_api, token_admin, mock_venda_service_api
):
    itens = [{'id_produto': 1, 'quantidade': 1}]
    mock_venda_service_api.realizar_venda.side_effect = LookupError(
        'Cliente nao encontrado.'
    )

    response = client_api.post(
        '/vendas/999/vender',
        json=itens,
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Cliente nao encontrado.'}


def test_cancelar_venda_retorna_404_se_service_retornar_lookup_error(
    client_api, token_admin, mock_venda_service_api
):
    mock_venda_service_api.cancelar_venda.side_effect = LookupError(
        'Venda nao encontrado.'
    )

    response = client_api.post(
        '/vendas/999/cancelar',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Venda nao encontrado.'}


def test_cancelar_venda_retorna_403_se_service_retornar_permission_error(
    client_api, token_funcionario, mock_venda_service_api
):
    mock_venda_service_api.cancelar_venda.side_effect = PermissionError(
        'Sem permissao para cancelar venda.'
    )

    response = client_api.post(
        '/vendas/999/cancelar',
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissao para cancelar venda.'}


def test_listar_venda_resumo_retorna_403_se_service_retornar_permission_error(
    client_api, token_funcionario, mock_venda_service_api
):
    mock_venda_service_api.listar_resumo.side_effect = PermissionError(
        'Sem permissao para listar.'
    )

    response = client_api.get(
        '/vendas/listar',
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissao para listar.'}


def test_listar_venda_detalhe_retorna_404_se_service_retornar_lookup_error(
    client_api, token_admin, mock_venda_service_api
):
    mock_venda_service_api.listar_venda_itens.side_effect = LookupError(
        'Venda nao encontrada.'
    )

    response = client_api.get(
        '/vendas/999/listar-detalhe',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Venda nao encontrada.'}


def test_listar_venda_detalhe_retorna_403_se_service_retornar_permission_error(
    client_api, token_funcionario, mock_venda_service_api
):
    mock_venda_service_api.listar_venda_itens.side_effect = PermissionError(
        'Sem permissao para listar.'
    )

    response = client_api.get(
        '/vendas/10/listar-detalhe',
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissao para listar.'}
