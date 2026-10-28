import factory
import pytest
from faker import Faker

from src.models import Cliente
from src.repositories.cliente_repository import ClienteRepository

fake = Faker('pt_BR')


class ClienteFatory(factory.Factory):
    class Meta:
        model = Cliente

    nome = factory.Faker('name')
    cpf = factory.Faker('cpf', locale='pt_BR')
    endereco = factory.Faker('address', locale='pt_BR')
    telefone = factory.LazyFunction(lambda: fake.numerify('###########'))
    ativo = True


@pytest.fixture
def client_repository(session):
    return ClienteRepository(session)
