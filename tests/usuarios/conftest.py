import factory
import factory.fuzzy
import pytest

from src.enums import PapelEnum
from src.models import Usuario
from src.repositories.usuario_repository import UsuarioRepository


class UserFactory(factory.Factory):
    class Meta:
        model = Usuario

    nome = factory.Faker('name')
    senha = factory.Faker('password')
    papel = factory.fuzzy.FuzzyChoice(PapelEnum)
    ativo = True


@pytest.fixture
def user_repository(session):
    repository = UsuarioRepository(session)
    return repository
