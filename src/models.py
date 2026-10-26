from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

from src.enums import PapelEnum


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class Usuario(Base):
    __tablename__ = 'usuarios'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    nome: Mapped[str]
    senha: Mapped[str]
    papel: Mapped[PapelEnum] = mapped_column(default=PapelEnum.FUNCIONARIO)
    ativo: Mapped[bool] = mapped_column(default=True)
