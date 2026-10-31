from sqlalchemy.orm import Session

from src.controllers.produto_controller import ProdutoController
from src.repositories.produto_repository import ProdutoRepository
from src.services.produto_service import ProdutoService


def product_controller(session: Session):
    produto_repo = ProdutoRepository(session)
    produto_serv = ProdutoService(produto_repo)

    return ProdutoController(produto_serv)
