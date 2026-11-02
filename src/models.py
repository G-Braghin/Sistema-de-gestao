from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

from src.enums import MotivoMovimentacao, PapelEnum, TipoMovimentacao


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
