from http import HTTPStatus


def test_cadastrar_produto_api(client_api, token_funcionario):
    response = client_api.post(
        '/produtos/cadastro',
        json={'nome': 'Teclado', 'preco': 10.99},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['id'] is not None
    assert response.json()['quantidade'] == 0
    assert response.json()['nome'] == 'TECLADO'
    assert response.json()['preco'] == 'R$ 10,99'


def test_atualizar_info_produto_api(client_api, token_funcionario, produto_db):
    response = client_api.patch(
        f'/produtos/{produto_db.id}/atualizar',
        json={'nome': 'Monitor', 'preco': None},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['id'] == produto_db.id
    assert response.json()['nome'] == 'MONITOR'
    assert response.json()['preco'] is not None


def test_listar_produtos_api(client_api, token_funcionario, produto_db):
    valor_formatado = (
        f'R$ {produto_db.preco:,.2f}'
        .replace(',', 'X')
        .replace('.', ',')
        .replace('X', '.')
    )
    response = client_api.get(
        '/produtos/listar', headers={'Authorization': f'Bearer {token_funcionario}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['produtos'] == [
        {
            'id': produto_db.id,
            'nome': produto_db.nome,
            'preco': valor_formatado,
            'quantidade': produto_db.quantidade,
        }
    ]


def test_atualizar_produto_retornar_404_se_service_retornar_lookup_error(
    client_api, token_funcionario
):
    response = client_api.patch(
        '/produtos/999999/atualizar',
        json={'nome': 'Monitor', 'preco': None},
        headers={'Authorization': f'Bearer {token_funcionario}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Produto nao encontrado!'}
