from decimal import Decimal

import factory
import pytest
from factory.declarations import SubFactory
from pytest_mock import MockerFixture

from src.enums import StatusVenda
from src.models import Venda, VendaItens
from src.repositories.venda_repository import VendaRepository
from src.services.venda_service import VendaService


class VendaItensFactory(factory.Factory):
    class Meta:
        model = VendaItens

    id_produto = 1
    preco_unitario = Decimal('10.00')
    quantidade = 3


class VendaFactory(factory.Factory):
    class Meta:
        model = Venda

    id_usuario = 1
    id_cliente = 1
    valor_total = Decimal('30.00')
    status = StatusVenda.CONCLUIDA
    itens = factory.List([SubFactory(VendaItensFactory)])


@pytest.fixture
def venda_repository(session):
    return VendaRepository(session)


@pytest.fixture
def mock_venda_repo(mocker: MockerFixture):
    return mocker.MagicMock(spec=VendaRepository)


@pytest.fixture
def venda_service(
    mock_venda_repo,
    product_repository_mock,
    client_repository_mock,
    mock_estoque_service,
):
    return VendaService(
        mock_venda_repo,
        product_repository_mock,
        client_repository_mock,
        mock_estoque_service,
    )


@pytest.fixture
def venda(session, cliente_db, usuario_db, produto_db):

    venda = VendaFactory(
        id_usuario=usuario_db.id,
        id_cliente=cliente_db.id,
        itens=[VendaItensFactory(id_produto=produto_db.id)],
    )
    session.add(venda)
    session.flush()

    return venda


@pytest.fixture
def venda_fake(user_gerente, cliente, produto):
    venda = VendaFactory(
        id_usuario=user_gerente.id,
        id_cliente=cliente.id,
        itens=[VendaItensFactory(id_produto=produto.id)],
    )
    venda.id = 99
    for item in venda.itens:
        item.id = 100

    return venda
