import factory
import pytest
from faker import Faker
from pytest_mock import MockerFixture

from src.models import Cliente
from src.repositories.cliente_repository import ClienteRepository
from src.services.cliente_service import ClienteService

fake = Faker('pt_BR')


class ClienteFatory(factory.Factory):
    class Meta:
        model = Cliente

    nome = factory.Faker('name', locale='pt_BR')
    cpf = factory.Faker('ssn', locale='pt_BR')
    endereco = factory.Faker('address', locale='pt_BR')
    telefone = factory.LazyFunction(lambda: fake.numerify('119########'))
    ativo = True


@pytest.fixture
def client_repository(session):
    return ClienteRepository(session)


@pytest.fixture
def client_service(client_repository_mock):
    return ClienteService(client_repository_mock)


@pytest.fixture
def client_repository_mock(mocker: MockerFixture):
    return mocker.MagicMock(spec=ClienteRepository)


@pytest.fixture
def cliente():
    client = ClienteFatory()
    client.id = 9
    return client


@pytest.fixture
def cliente_inativo():
    client = ClienteFatory(ativo=False)
    client.id = 11
    return client


def criar_client(**kwargs):
    client = ClienteFatory(**kwargs)
    client.id = 5
    return client
