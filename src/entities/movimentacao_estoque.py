from datetime import datetime, timezone

from src.entities.enums.motivo_movimentacao import MotivoMovimentacao
from src.entities.enums.tipo_movimentacao import TipoMovimentacao


class MovimentacaoEstoque:
    def __init__(
        self,
        id_produto: int,
        id_usuario: int,
        tipo: TipoMovimentacao,
        quantidade: int,
        motivo: MotivoMovimentacao,
        data_hora: datetime | None = None,
        id_movimentacao: int | None = None,
        id_venda: int | None = None,
    ):
        self.id_produto = id_produto
        self.id_usuario = id_usuario
        self.tipo = tipo
        self.id_movimentacao = id_movimentacao
        self.quantidade = quantidade
        self.motivo = motivo
        self.id_venda = id_venda
        self.data_hora = (
            data_hora if data_hora is not None else datetime.now(timezone.utc)
        )

    def __str__(self):
        return f"MovimentacaoEstoque(id_movimentacao={self.id_movimentacao},id_produto={self.id_produto}, tipo={self.tipo}, quantidade={self.quantidade})"
