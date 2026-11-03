from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Movimentacao


class MovimentacaoRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar(self, movimentacao: Movimentacao) -> Movimentacao:
        """Cria a os dados de uma movimentacao na tabela."""
        self.session.add(movimentacao)
        self.session.flush()

        return movimentacao

    def buscar_por_id(self, id_movimentacao) -> Movimentacao | None:
        """Buscar por uma movimentacao pelo id na tabela."""
        movimentacao = self.session.scalar(
            select(Movimentacao).where(Movimentacao.id == id_movimentacao)
        )

        return movimentacao

    def listar(self) -> list[Movimentacao]:
        """Lista as movimentacoes realizadas registradas na tabela."""
        query = select(Movimentacao).order_by(Movimentacao.created_at.desc())
        movimentacao = list(self.session.scalars(query).all())

        return movimentacao
