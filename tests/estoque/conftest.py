import factory
import factory.fuzzy
import pytest
from pytest_mock import MockerFixture

from src.enums import MotivoMovimentacao, TipoMovimentacao
from src.models import Movimentacao
from src.repositories.movimentacao_repository import MovimentacaoRepository
from src.repositories.produto_repository import ProdutoRepository
from src.services.estoque_service import EstoqueService


class MovFactory(factory.Factory):
    """Deve sempre receber id_produto e id_usuario."""

    class Meta:
        model = Movimentacao

    # ids placeholder apenas
    id_produto = 1
    id_usuario = 1
    tipo_movimentacao = factory.fuzzy.FuzzyChoice(TipoMovimentacao)
    motivo = factory.fuzzy.FuzzyChoice(MotivoMovimentacao)
    quantidade = factory.Faker('random_int', min=1, max=50)


@pytest.fixture
def mov_repository(session):
    return MovimentacaoRepository(session)


@pytest.fixture
def mock_mov_repository(mocker: MockerFixture):
    return mocker.MagicMock(spec=MovimentacaoRepository)


@pytest.fixture
def mock_product_repository(mocker: MockerFixture):
    return mocker.MagicMock(spec=ProdutoRepository)


@pytest.fixture
def estoque_service(mock_mov_repository, mock_product_repository):
    return EstoqueService(mock_product_repository, mock_mov_repository)
