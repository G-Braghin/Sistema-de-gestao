import factory
import factory.fuzzy
import pytest

from src.enums import MotivoMovimentacao, TipoMovimentacao
from src.main import MovimentacaoRepository
from src.models import Movimentacao


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
