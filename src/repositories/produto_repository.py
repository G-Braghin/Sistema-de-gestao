from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Produto


class ProdutoRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar(self, produto: Produto) -> Produto:
        self.session.add(produto)
        self.session.flush()

        return produto

    def buscar_por_id(self, id_produto: int) -> Produto | None:
        """Busca padrao para consultas"""

        produto = self.session.scalar(select(Produto).where(Produto.id == id_produto))
        return produto

    def buscar_por_id_para_atualizar(self, id_produto: int) -> Produto | None:
        """Busca feita para processos de escrita(ex: atualizar estoque)"""

        produto = self.session.scalar(
            select(Produto).where(Produto.id == id_produto).with_for_update()
        )
        return produto

    def buscar_por_multiplos_ids(self, lista_ids: list[int]) -> list[Produto]:
        """Busca feita para processos de escrita com varios itens"""

        if not lista_ids:
            return []

        ids_ordenados = sorted(lista_ids)

        query = select(Produto).where(Produto.id.in_(ids_ordenados)).with_for_update()
        produtos = list(self.session.scalars(query).all())

        return produtos

    def listar(self) -> list[Produto]:
        produtos = self.session.scalars(select(Produto)).all()

        return produtos

    def atualizar(self, produto: Produto) -> Produto:
        self.session.merge(produto)

        return produto
