from sqlalchemy.orm import Session

from src.controllers.usuario_controller import UsuarioController
from src.repositories.usuario_repository import UsuarioRepository
from src.services.autenticacao_service import AutenticacaoService
from src.services.usuario_service import UsuarioService


def user_controler(session: Session) -> UsuarioController:

    usuario_repo = UsuarioRepository(session)
    autenticacao_serv = AutenticacaoService(usuario_repo)
    usuario_serv = UsuarioService(usuario_repo, autenticacao_serv)

    return UsuarioController(usuario_serv, autenticacao_serv)
