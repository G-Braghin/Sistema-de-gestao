import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from src.api.app import app
from src.api.dependencies.services import get_autenticacao_service
from src.api.security import criar_token
from src.services.autenticacao_service import AutenticacaoService
from src.settings import Settings


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def token(user_funcionario):
    return criar_token(user_funcionario.id)


@pytest.fixture
def api_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_auth_service(mocker: MockerFixture):
    mock_autenticacao = mocker.MagicMock(spec=AutenticacaoService)

    app.dependency_overrides[get_autenticacao_service] = lambda: mock_autenticacao

    yield mock_autenticacao

    app.dependency_overrides.clear()
