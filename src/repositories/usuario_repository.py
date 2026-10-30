from sqlalchemy import Case, exists, select
from sqlalchemy.orm import Session

from src.enums import PapelEnum
from src.models import Usuario


class UsuarioRepository:
    def __init__(self, session: Session):
        self.session = session

    def buscar_por_id(self, user_id: int) -> Usuario:
        usuario = self.session.scalar(select(Usuario).where(Usuario.id == user_id))
        return usuario

    def criar(self, usuario: Usuario) -> Usuario:
        self.session.add(usuario)
        self.session.flush()
        return usuario

    def atualizar(self, user_id, novos_dados: dict) -> Usuario | None:
        usuario = self.buscar_por_id(user_id)

        if not usuario:
            return None

        for campo, valor in novos_dados.items():
            setattr(usuario, campo, valor)

        self.session.flush()
        return usuario

    def listar(self, status_ativo: bool = True):
        query = select(Usuario).where(Usuario.ativo == status_ativo)
        query = query.order_by(
            Case(
                (Usuario.papel == PapelEnum.ADMIN, 1),
                (Usuario.papel == PapelEnum.GERENTE, 2),
                (Usuario.papel == PapelEnum.FUNCIONARIO, 3),
                else_=4,
            ),
            Usuario.nome.asc(),
        )
        usuarios = self.session.scalars(query).all()
        return usuarios

    def existe_usuario(self):
        query = exists(select(1).select_from(Usuario)).select()
        existe = self.session.scalar(query)
        return existe
