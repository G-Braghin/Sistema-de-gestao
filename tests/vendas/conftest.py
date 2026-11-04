from decimal import Decimal

import factory
import pytest
from factory.declarations import SubFactory
from pytest_mock import MockerFixture

from src.enums import StatusVenda
from src.models import Venda, VendaItens
from src.repositories.venda_repository import VendaRepository


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


def mock_venda_repo(mocker: MockerFixture):
    return mocker.MagicMock(spec=VendaRepository)


def venda_service():
    

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
