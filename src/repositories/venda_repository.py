from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.entities.dtos.produtos_vendidos_resumo import ProdutosVendidosResumo
from src.entities.dtos.venda_resumo import VendaResumo
from src.enums import StatusVenda
from src.models import Cliente, Produto, Usuario, Venda, VendaItens


class VendaRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar(self, venda: Venda) -> Venda:
        self.session.add(venda)
        self.session.flush()

        return venda

    def buscar_por_id(self, id_venda: int) -> Venda | None:
        venda = self.session.scalar(select(Venda).where(Venda.id == id_venda))

        return venda

    def listar_resumo(
        self,
        data_inicio: date,
        data_fim: date,
        venda_status: StatusVenda | None = None,
    ) -> list[VendaResumo]:
        query = (
            select(
                Venda.id.label('id_venda'),
                Cliente.nome.label('nome_cliente'),
                Usuario.nome.label('nome_vendedor'),
                Venda.status,
                Venda.valor_total,
                Venda.created_at.label('data_venda'),
            )
            .join(Cliente, Venda.id_cliente == Cliente.id)
            .join(Usuario, Venda.id_usuario == Usuario.id)
            .where(Venda.created_at >= data_inicio, Venda.created_at < data_fim)
        )

        if venda_status is not None:
            query = query.where(Venda.status == venda_status)

        query = query.order_by(Venda.created_at.desc())
        resultados = self.session.execute(query).mappings().all()

        return [VendaResumo(**resultado) for resultado in resultados]

    def cancelar_venda(self, id_venda: int) -> None | Venda:
        venda = self.session.get(Venda, id_venda)

        if venda is None:
            return None

        if venda.status != StatusVenda.CONCLUIDA:
            return None

        venda.status = StatusVenda.CANCELADA

        return venda

    def listar_produtos_mais_vendidos(
        self, data_inicio: date, data_fim: date
    ) -> list[ProdutosVendidosResumo]:
        total_vendido = func.sum(VendaItens.quantidade).label('total_vendido')
        faturamento_total = func.sum(
            VendaItens.quantidade * VendaItens.preco_unitario
        ).label('faturamento_total')

        query = (
            select(
                Produto.id.label('id_produto'),
                Produto.nome.label('nome_produto'),
                total_vendido.label('quantidade_vendida'),
                faturamento_total.label('valor_total'),
            )
            .join(Produto, VendaItens.id_produto == Produto.id)
            .join(Venda, VendaItens.id_venda == Venda.id)
        )

        query = query.where(
            Venda.status == StatusVenda.CONCLUIDA,
            Venda.created_at >= data_inicio,
            Venda.created_at < data_fim,
        )
        query = query.group_by(Produto.id, Produto.nome)

        query = query.order_by(
            total_vendido.desc(),
            faturamento_total.desc(),
            Produto.nome.asc(),
            Produto.id.asc(),
        )

        resultados = self.session.execute(query).mappings().all()

        return [ProdutosVendidosResumo(**resultado) for resultado in resultados]
