from datetime import timezone
from http import HTTPStatus
from zoneinfo import ZoneInfo

from src.enums import MotivoMovimentacao, TipoMovimentacao


def test_entrada_estoque_api(client_api, token_admin, produto_db, admin):
    response = client_api.post(
        f'/estoque/{produto_db.id}/entrada',
        json={'quantidade': 10, 'motivo': MotivoMovimentacao.REPOSICAO},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['id'] is not None
    assert response.json()['tipo_movimentacao'] == TipoMovimentacao.ENTRADA
    assert response.json()['motivo'] == MotivoMovimentacao.REPOSICAO
    assert response.json()['id_produto'] == produto_db.id
    assert response.json()['id_usuario'] == admin.id


def test_saida_estoque_api(client_api, token_admin, produto_db, admin):
    response = client_api.post(
        f'/estoque/{produto_db.id}/saida',
        json={'quantidade': 2, 'motivo': MotivoMovimentacao.AJUSTE},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['id'] is not None
    assert response.json()['tipo_movimentacao'] == TipoMovimentacao.SAIDA
    assert response.json()['motivo'] == MotivoMovimentacao.AJUSTE
    assert response.json()['id_produto'] == produto_db.id
    assert response.json()['id_usuario'] == admin.id


def test_listar_movimentacao_api(client_api, token_admin, movimentacao):
    data_formatada = (
        movimentacao.created_at
        .replace(tzinfo=timezone.utc)
        .astimezone(ZoneInfo('America/Sao_Paulo'))
        .strftime('%d/%m/%Y %H:%M')
    )

    response = client_api.get(
        '/estoque/listar',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['movimentacoes'] == [
        {
            'id': movimentacao.id,
            'id_produto': movimentacao.id_produto,
            'id_usuario': movimentacao.id_usuario,
            'quantidade': movimentacao.quantidade,
            'tipo_movimentacao': movimentacao.tipo_movimentacao.value,
            'motivo': movimentacao.motivo.value,
            'created_at': data_formatada,
            'id_venda': None,
        }
    ]


def test_entrada_estoque_retorna_404_se_service_retornar_lookup_error(
    client_api, token_admin
):
    response = client_api.post(
        '/estoque/999/entrada',
        json={'quantidade': 10, 'motivo': MotivoMovimentacao.REPOSICAO},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Produto nao encontrado!'}


def test_entrada_estoque_retorna_403_se_service_retornar_permission_error(
    client_api, token_funcionario
):
    response = client_api.post(
        '/estoque/10/entrada',
        json={'quantidade': 10, 'motivo': MotivoMovimentacao.REPOSICAO},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissao para mecher no estoque'}


def test_entrada_saida_retornar_400_se_service_retornar_value_error(
    client_api, token_admin, produto_db
):
    response = client_api.post(
        f'/estoque/{produto_db.id}/saida',
        json={'quantidade': 100, 'motivo': MotivoMovimentacao.AJUSTE},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'detail': f'Estoque indisponivel! Disponivel {produto_db.quantidade}.'
    }


def test_entrada_saida_retornar_404_se_service_retornar_lookup_error(
    client_api, token_admin
):
    response = client_api.post(
        '/estoque/999/saida',
        json={'quantidade': 10, 'motivo': MotivoMovimentacao.AJUSTE},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Produto nao encontrado!'}


def test_entrada_saida_retornar_403_se_service_retornar_permission_error(
    client_api, token_funcionario
):
    response = client_api.post(
        '/estoque/10/saida',
        json={'quantidade': 10, 'motivo': MotivoMovimentacao.AJUSTE},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissao para mecher no estoque'}


def test_listar_movimentacao_retorna_403_se_service_retornar_permission_error(
    client_api, token_funcionario
):
    response = client_api.get(
        '/estoque/listar',
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para ver o histórico de movimentações.'
    }
