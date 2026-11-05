from sqlalchemy.orm import Session

from src.controllers.venda_controller import VendaController
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.movimentacao_repository import MovimentacaoRepository
from src.repositories.produto_repository import ProdutoRepository
from src.repositories.venda_repository import VendaRepository
from src.services.estoque_service import EstoqueService
from src.services.venda_service import VendaService


def get_venda_controller(session: Session):
    client_repo = ClienteRepository(session)
    produto_repo = ProdutoRepository(session)
    venda_repo = VendaRepository(session)
    movimentacao_repo = MovimentacaoRepository(session)
    estoque_serv = EstoqueService(produto_repo, movimentacao_repo)
    venda_serv = VendaService(venda_repo, produto_repo, client_repo, estoque_serv)

    return VendaController(venda_serv)
