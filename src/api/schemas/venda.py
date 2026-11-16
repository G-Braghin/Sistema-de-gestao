from datetime import date

from pydantic import BaseModel, Field, model_validator

from src.api.schemas.types import FormatarHora, FormatarPreco
from src.enums import StatusVenda
from src.utils.filtro_datas import FiltroDatas


# Entrada
class VendaItem(BaseModel):
    id_produto: int = Field(gt=0)
    quantidade: int = Field(gt=0)


# Filtro
class VendaResumoFiltro(BaseModel):
    status_venda: StatusVenda | None = None
    filtro_data: FiltroDatas = FiltroDatas.MES_ATUAL
    inicio_filtro: date | None = None
    final_filtro: date | None = None

    @model_validator(mode='after')
    def validar_datas_personalizadas(self):
        if self.filtro_data != FiltroDatas.PERSONALIZADO:
            self.inicio_filtro = None
            self.final_filtro = None
            return self

        if self.filtro_data == FiltroDatas.PERSONALIZADO:
            if self.inicio_filtro is None or self.final_filtro is None:
                raise ValueError(
                    'As datas inicial e final são obrigatórias '
                    'para o filtro personalizado.'
                )

            if self.inicio_filtro > self.final_filtro:
                raise ValueError('A data inicial não pode ser posterior à data final.')

        return self


# Saida
class VendaItemResponse(BaseModel):
    id: int
    id_produto: int
    quantidade: int
    preco_unitario: FormatarPreco


class VendaResponse(BaseModel):
    id: int
    id_cliente: int
    id_usuario: int
    valor_total: FormatarPreco
    status: StatusVenda
    created_at: FormatarHora
    itens: list[VendaItemResponse] = []


class VendaListagem(BaseModel):
    id_venda: int
    nome_cliente: str
    nome_vendedor: str
    data_venda: FormatarHora
    valor_total: FormatarPreco
    status: StatusVenda


class VendaLista(BaseModel):
    vendas: list[VendaListagem]
