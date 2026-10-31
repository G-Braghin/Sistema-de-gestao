import factory
import pytest
from pytest_mock import MockerFixture

from src.models import Produto
from src.repositories.produto_repository import ProdutoRepository
from src.services.produto_service import ProdutoService


class ProductFactory(factory.Factory):
    class Meta:
        model = Produto

    nome = factory.Faker('word', locale='pt_BR')
    preco = factory.Faker('pyfloat', right_digits=2, min_value=10, max_value=1000)
    quantidade = factory.Faker('random_int', min=1, max=50)


@pytest.fixture
def product_repository(session):
    return ProdutoRepository(session)


@pytest.fixture
def product_repository_mock(mocker: MockerFixture):
    return mocker.MagicMock(spec=ProdutoRepository)


@pytest.fixture
def product_service(product_repository_mock):
    return ProdutoService(product_repository_mock)


@pytest.fixture
def produto_db(session):
    produto = ProductFactory()
    session.add(produto)
    session.commit()

    return produto


@pytest.fixture
def produtos_db(session):
    produtos = ProductFactory.build_batch(3)
    session.add_all(produtos)
    session.commit()

    return produtos


@pytest.fixture
def produto():
    produto = ProductFactory()
    produto.id = 99
    return produto
