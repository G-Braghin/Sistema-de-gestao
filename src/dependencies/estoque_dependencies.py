from sqlalchemy.orm import Session

from src.controllers.estoque_controller import EstoqueController
from src.repositories.movimentacao_repository import MovimentacaoRepository
from src.repositories.produto_repository import ProdutoRepository
from src.services.estoque_service import EstoqueService


def get_estoque_controller(session: Session):
    movimentacao_repo = MovimentacaoRepository(session)
    produto_repo = ProdutoRepository(session)
    estoque_serv = EstoqueService(produto_repo, movimentacao_repo)

    return EstoqueController(estoque_serv)
