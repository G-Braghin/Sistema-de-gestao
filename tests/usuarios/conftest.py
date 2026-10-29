import factory
import factory.fuzzy
import pytest
from pytest_mock import MockerFixture

from src.enums import PapelEnum
from src.models import Usuario
from src.repositories.usuario_repository import UsuarioRepository
from src.services.autenticacao_service import AutenticacaoService
from src.services.usuario_service import UsuarioService


class UserFactory(factory.Factory):
    class Meta:
        model = Usuario

    nome = factory.Faker('name')
    senha = factory.Faker('password')
    papel = factory.fuzzy.FuzzyChoice(PapelEnum)
    ativo = True


@pytest.fixture
def user_repository(session):
    return UsuarioRepository(session)


@pytest.fixture
def user_service(user_repository_mock, user_auth_mock):
    return UsuarioService(user_repository_mock, user_auth_mock)


@pytest.fixture
def user_auth(user_repository_mock):
    return AutenticacaoService(user_repository_mock)


@pytest.fixture
def user_repository_mock(mocker: MockerFixture):
    return mocker.MagicMock(spec=UsuarioRepository)


@pytest.fixture
def user_auth_mock(mocker: MockerFixture):
    return mocker.MagicMock(spec=AutenticacaoService)


def usuario_criar(**kwargs):
    senha_limpa = 'senha-limpa'
    usuario = UserFactory(
        senha=AutenticacaoService.gerar_senha_hash(senha_limpa), **kwargs
    )
    usuario.id = 10
    usuario.senha_limpa = senha_limpa
    return usuario


@pytest.fixture
def usuario():
    return usuario_criar()
