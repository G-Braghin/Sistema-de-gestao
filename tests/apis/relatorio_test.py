from http import HTTPStatus


def test_relatorio_venda_resumo_vazio_api(client_api, token_admin):
    periodo = {'inicio': '2026-01-01', 'fim': '2026-12-31'}
    response = client_api.get(
        '/relatorios/venda-resumo',
        params=periodo,
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'data_inicial': '01/01/2026 00:00',
        'data_final': '31/12/2026 00:00',
        'vendas_concluidas': 0,
        'total_periodo': 'R$ 0,00',
        'ticket_medio': 'R$ 0,00',
    }


def test_relatorio_produtos_mais_vendidos_api(
    client_api, token_admin, venda, produto_db
):
    periodo = {'inicio': '2026-01-01', 'fim': '2026-12-31'}

    valor_formatado = (
        f'R$ {venda.valor_total:,.2f}'
        .replace(',', 'X')
        .replace('.', ',')
        .replace('X', '.')
    )
    quantidade = [item.quantidade for item in venda.itens]
    response = client_api.get(
        '/relatorios/produtos-vendidos',
        params=periodo,
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['produtos'] == [
        {
            'id_produto': produto_db.id,
            'nome_produto': produto_db.nome,
            'quantidade_vendida': quantidade[0],
            'valor_total': valor_formatado,
        }
    ]


def test_relatorio_estoque_api(client_api, token_admin, produto_db):
    valor_formatado = (
        f'R$ {produto_db.preco:,.2f}'
        .replace(',', 'X')
        .replace('.', ',')
        .replace('X', '.')
    )

    response = client_api.get(
        '/relatorios/estoque',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'produtos': [
            {
                'id': produto_db.id,
                'nome': produto_db.nome,
                'preco': valor_formatado,
                'quantidade': produto_db.quantidade,
            },
        ],
        'quantidade_produtos_cadastrados': 1,
        'total_unidades_estoque': produto_db.quantidade,
        'quantidade_produtos_sem_estoque': 0,
    }


def test_relatorio_estoque_baixo_api(client_api, token_admin, produto_db):
    valor_formatado = (
        f'R$ {produto_db.preco:,.2f}'
        .replace(',', 'X')
        .replace('.', ',')
        .replace('X', '.')
    )

    response = client_api.get(
        '/relatorios/estoque-limite',
        params={'limite': produto_db.quantidade},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['produtos'] == [
        {
            'id': produto_db.id,
            'nome': produto_db.nome,
            'preco': valor_formatado,
            'quantidade': produto_db.quantidade,
        },
    ]


def test_relatorio_venda_resumo_retorna_403_se_service_retornar_permission_error(
    client_api, token_funcionario, mock_venda_service_api
):
    periodo = {'inicio': '2026-01-01', 'fim': '2026-12-31'}
    mock_venda_service_api.criar_resumo_relatorio.side_effect = PermissionError(
        'Sem permissao'
    )
    response = client_api.get(
        '/relatorios/venda-resumo',
        params=periodo,
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissao'}


def test_relatorio_mais_vendidos_retorna_403_se_service_retornar_permission_error(
    client_api, token_funcionario, mock_venda_service_api
):
    periodo = {'inicio': '2026-01-01', 'fim': '2026-12-31'}
    mock_venda_service_api.relatorio_produtos.side_effect = PermissionError(
        'Sem permissao'
    )
    response = client_api.get(
        '/relatorios/produtos-vendidos',
        params=periodo,
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissao'}


def test_relatorio_estoque_retorna_403_se_service_retornar_permission_error(
    client_api, token_funcionario, mock_estoque_service_api
):
    mock_estoque_service_api.relatorio_estoque.side_effect = PermissionError(
        'Sem permissao'
    )
    response = client_api.get(
        '/relatorios/estoque',
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissao'}


def test_relatorio_estoque_baixo_retorna_403_se_service_retornar_permission_error(
    client_api, token_funcionario, mock_estoque_service_api
):
    mock_estoque_service_api.relatorio_estoque_baixo.side_effect = PermissionError(
        'Sem permissao'
    )
    response = client_api.get(
        '/relatorios/estoque-limite',
        params={'limite': 10},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissao'}
