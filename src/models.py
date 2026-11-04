from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)

from src.enums import MotivoMovimentacao, PapelEnum, StatusVenda, TipoMovimentacao


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class Usuario(Base):
    __tablename__ = 'usuarios'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    nome: Mapped[str]
    senha: Mapped[str]
    papel: Mapped[PapelEnum] = mapped_column(
        Enum(PapelEnum), default=PapelEnum.FUNCIONARIO
    )
    ativo: Mapped[bool] = mapped_column(default=True)


class Cliente(Base):
    __tablename__ = 'clientes'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    nome: Mapped[str]
    cpf: Mapped[str] = mapped_column(unique=True)
    telefone: Mapped[str | None] = mapped_column(default=None)
    endereco: Mapped[str | None] = mapped_column(default=None)
    ativo: Mapped[bool] = mapped_column(default=True)


class Produto(Base):
    __tablename__ = 'produtos'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    nome: Mapped[str]
    preco: Mapped[Decimal]
    quantidade: Mapped[int] = mapped_column(default=0)


class Movimentacao(Base):
    __tablename__ = 'movimentacoes'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    id_produto: Mapped[int] = mapped_column(ForeignKey('produtos.id'))
    id_usuario: Mapped[int] = mapped_column(ForeignKey('usuarios.id'))
    tipo_movimentacao: Mapped[TipoMovimentacao]
    motivo: Mapped[MotivoMovimentacao]
    quantidade: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), init=False)
    id_venda: Mapped[int | None] = mapped_column(ForeignKey('vendas.id'), default=None)


class Venda(Base):
    __tablename__ = 'vendas'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    id_cliente: Mapped[int] = mapped_column(ForeignKey('clientes.id'))
    id_usuario: Mapped[int] = mapped_column(ForeignKey('usuarios.id'))

    valor_total: Mapped[Decimal]
    status: Mapped[StatusVenda]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), init=False)

    itens: Mapped[list[VendaItens]] = relationship(
        cascade='all, delete-orphan', lazy='selectin'
    )


class VendaItens(Base):
    __tablename__ = 'venda_itens'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    id_venda: Mapped[int] = mapped_column(ForeignKey('vendas.id'), init=False)
    id_produto: Mapped[int] = mapped_column(ForeignKey('produtos.id'))
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    quantidade: Mapped[int]

    @property
    def subtotal(self) -> Decimal:
        return self.preco_unitario * self.quantidade
