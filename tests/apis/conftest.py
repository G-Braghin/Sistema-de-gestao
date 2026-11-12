import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from src.api.app import app
from src.api.dependencies.services import (
    get_autenticacao_service,
    get_cliente_service,
    get_usuario_service,
)
from src.api.security import criar_token
from src.database.database import get_session
from src.main import PapelEnum
from src.services.autenticacao_service import AutenticacaoService
from src.services.cliente_service import ClienteService
from src.services.usuario_service import UsuarioService
from src.settings import Settings
from tests.conftest import ClienteFatory
from tests.usuarios.conftest import UserFactory


@pytest.fixture
def client_api(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def admin(session):
    senha_limpa = 'senha'

    usuario = UserFactory(
        senha=AutenticacaoService.gerar_senha_hash(senha_limpa), papel=PapelEnum.ADMIN
    )

    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    usuario.senha_limpa = senha_limpa

    return usuario


@pytest.fixture
def funcionario(session):
    senha_limpa = 'senha'

    usuario = UserFactory(
        senha=AutenticacaoService.gerar_senha_hash(senha_limpa),
        papel=PapelEnum.FUNCIONARIO,
    )

    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    usuario.senha_limpa = senha_limpa

    return usuario


@pytest.fixture
def funcionario_inativo(session):
    senha_limpa = 'senha'

    usuario = UserFactory(
        senha=AutenticacaoService.gerar_senha_hash(senha_limpa),
        papel=PapelEnum.FUNCIONARIO,
        ativo=False,
    )

    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    usuario.senha_limpa = senha_limpa

    return usuario


@pytest.fixture
def token_falso():
    token = criar_token(99)
    return token


@pytest.fixture
def token_admin(client_api, admin):
    response = client_api.post(
        '/autenticacao/login',
        data={'username': admin.id, 'password': admin.senha_limpa},
    )

    return response.json()['access_token']


@pytest.fixture
def token_funcionario(client_api, funcionario):
    response = client_api.post(
        '/autenticacao/login',
        data={
            'username': funcionario.id,
            'password': funcionario.senha_limpa,
        },
    )

    return response.json()['access_token']


@pytest.fixture
def mock_auth_service(mocker: MockerFixture):
    mock_autenticacao = mocker.MagicMock(spec=AutenticacaoService)

    app.dependency_overrides[get_autenticacao_service] = lambda: mock_autenticacao

    yield mock_autenticacao

    app.dependency_overrides.clear()


@pytest.fixture
def mock_usuario_service_api(mocker: MockerFixture):
    mock_service = mocker.MagicMock(spec=UsuarioService)

    app.dependency_overrides[get_usuario_service] = lambda: mock_service

    yield mock_service

    app.dependency_overrides.clear()


@pytest.fixture
def mock_cliente_service_api(mocker: MockerFixture):
    mock_service = mocker.MagicMock(spec=ClienteService)

    app.dependency_overrides[get_cliente_service] = lambda: mock_service

    yield mock_service

    app.dependency_overrides.clear()
