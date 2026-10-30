from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Cliente


class ClienteRepository:
    def __init__(self, session: Session):
        self.session = session

    def buscar_por_id(self, client_id) -> Cliente | None:
        cliente = self.session.scalar(select(Cliente).where(Cliente.id == client_id))
        return cliente

    def buscar_por_cpf(self, client_cpf: str) -> Cliente | None:
        cliente = self.session.scalar(select(Cliente).where(Cliente.cpf == client_cpf))
        return cliente

    def criar(self, cliente: Cliente) -> Cliente:
        self.session.add(cliente)
        self.session.flush()

        return cliente

    def atualizar(self, cliente: Cliente) -> Cliente:
        cliente_atualizado = self.session.merge(cliente)
        self.session.flush()

        return cliente_atualizado

    def listar(self, status_ativo: bool = True) -> list[Cliente]:
        query = select(Cliente).where(Cliente.ativo == status_ativo)
        query = query.order_by(Cliente.nome)
        lista_clientes = self.session.scalars(query).all()

        return lista_clientes
