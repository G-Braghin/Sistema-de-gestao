from sqlalchemy.orm import Session

from src.controllers.cliente_controller import ClienteController
from src.repositories.cliente_repository import ClienteRepository
from src.services.cliente_service import ClienteService


def client_controller(session: Session):
    cliente_repo = ClienteRepository(session)
    cliente_serv = ClienteService(cliente_repo)

    return ClienteController(cliente_serv)
