from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from src.entities.dtos.produtos_vendidos_resumo import ProdutosVendidosResumo
from src.entities.dtos.relatorio_venda_resumo import RelatorioVendaResumo
from src.entities.dtos.venda_resumo import VendaResumo
from src.enums import MotivoMovimentacao, PapelEnum, StatusVenda
from src.models import Usuario, Venda, VendaItens
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.produto_repository import ProdutoRepository
from src.repositories.venda_repository import VendaRepository
from src.services.estoque_service import EstoqueService
from src.utils.filtro_datas import FiltroDatas
from src.utils.fuso import FUSO_HORARIO

MES_DEZEMBRO = 12


class VendaService:
    def __init__(
        self,
        venda_repository: VendaRepository,
        produto_repository: ProdutoRepository,
        cliente_repository: ClienteRepository,
        estoque_service: EstoqueService,
    ):
        self.venda_repository = venda_repository
        self.produto_repository = produto_repository
        self.cliente_repository = cliente_repository
        self.estoque_service = estoque_service

    def realizar_venda(
        self,
        usuario_logado: Usuario,
        id_cliente: int,
        itens: list[dict],
    ) -> Venda:
        cliente = self.cliente_repository.buscar_por_id(id_cliente)

        if not cliente:
            raise LookupError('Cliente nao encontrado.')

        if not cliente.ativo:
            raise ValueError('Cliente nao pode estar desativado.')

        venda_itens = self._criar_itens_venda(itens)

        total = sum(
            (item.subtotal for item in venda_itens),
            start=Decimal('0.00'),
        )

        venda = Venda(
            id_cliente=id_cliente,
            id_usuario=usuario_logado.id,
            itens=venda_itens,
            valor_total=total,
            status=StatusVenda.CONCLUIDA,
        )

        self.venda_repository.criar(venda)

        for item in venda_itens:
            self.estoque_service.dar_saida(
                usuario_logado=usuario_logado,
                id_produto=item.id_produto,
                saida_estoque=item.quantidade,
                motivo=MotivoMovimentacao.VENDA,
                id_venda=venda.id,
            )

        return venda

    def _criar_itens_venda(self, itens: list[dict]) -> list[VendaItens]:
        if not itens:
            raise ValueError('Ao menos deve ter um item.')

        return [self._criar_item_venda(item) for item in itens]

    def _criar_item_venda(self, item: dict) -> VendaItens:

        if 'id_produto' not in item:
            raise ValueError('O produto deve ter um ID obrigatorio')

        if 'quantidade' not in item:
            raise ValueError('O produto deve ter uma quantidade.')

        quantidade = item['quantidade']
        id_produto = item['id_produto']

        produto = self.produto_repository.buscar_por_id_para_atualizar(id_produto)
        if not produto:
            raise LookupError(f'Produto de id: {id_produto} nao encontrado')

        if not self.estoque_service.validar_disponibilidade(id_produto, quantidade):
            raise ValueError(
                f'Estoque insuficiente para o produto: {produto.nome} '
                f'Disponivel: {produto.quantidade}'
            )

        return VendaItens(
            id_produto=id_produto,
            quantidade=quantidade,
            preco_unitario=produto.preco,
        )

    def cancelar_venda(
        self,
        usuario_logado: Usuario,
        id_venda: int,
    ) -> Venda:

        if usuario_logado.papel == PapelEnum.FUNCIONARIO:
            raise PermissionError('Sem permissao para cancelar vendas.')

        venda = self.venda_repository.buscar_por_id(id_venda)
        if venda is None:
            raise LookupError('ID nao encontrado!')

        self.venda_repository.cancelar_venda(
            id_venda=id_venda,
        )

        for item in sorted(venda.itens, key=lambda item: item.id_produto):
            self.estoque_service.dar_entrada(
                usuario_logado=usuario_logado,
                id_produto=item.id_produto,
                entrada_estoque=item.quantidade,
                motivo=MotivoMovimentacao.CANCELAMENTO_VENDA,
                id_venda=item.id_venda,
            )

        return venda

    def listar_resumo(
        self,
        usuario_logado: Usuario,
        status_venda: StatusVenda | None = None,
        filtro_data: FiltroDatas | None = None,
        inicio_filtro: date | None = None,
        final_filtro: date | None = None,
    ) -> list[VendaResumo]:
        if usuario_logado.papel == PapelEnum.FUNCIONARIO:
            raise PermissionError('Sem permissao para ver lista vendas.')

        if filtro_data is None:
            filtro_data = FiltroDatas.MES_ATUAL

        data_inicial, data_final = self._obter_intervalo_filtro_datas(
            filtro_data, inicio_filtro, final_filtro
        )

        vendas = self.venda_repository.listar_resumo(
            data_inicial, data_final, status_venda
        )

        return vendas

    def listar_venda_itens(self, usuario_logado: Usuario, id_venda: int) -> Venda:
        if usuario_logado.papel == PapelEnum.FUNCIONARIO:
            raise PermissionError('Sem Permissao para ver venda de itens.')

        vendas = self.venda_repository.buscar_por_id(id_venda)
        if vendas is None:
            raise LookupError('ID nao encontrado.')

        return vendas

    def criar_resumo_relatorio(
        self, usuario_logado: Usuario, data_inicial: date, data_final: date
    ) -> RelatorioVendaResumo:
        if usuario_logado.papel == PapelEnum.FUNCIONARIO:
            raise PermissionError('Sem permissao para ver relatorios.')

        inicio, final = self._obter_intervalo_filtro_datas(
            FiltroDatas.PERSONALIZADO, data_inicial, data_final
        )

        vendas = self.venda_repository.listar_resumo(
            inicio, final, StatusVenda.CONCLUIDA
        )

        num_vendas_concluidas = len(vendas)
        total_periodo = sum((venda.valor_total for venda in vendas), Decimal('0'))
        ticket_medio = (
            total_periodo / num_vendas_concluidas
            if num_vendas_concluidas > 0
            else Decimal('0')
        )

        relatorio = RelatorioVendaResumo(
            data_inicial=data_inicial,
            data_final=data_final,
            vendas_concluidas=num_vendas_concluidas,
            total_periodo=total_periodo,
            ticket_medio=ticket_medio,
        )

        return relatorio

    def relatorio_produtos(
        self, usuario_logado: Usuario, data_inicial: date, data_final: date
    ) -> list[ProdutosVendidosResumo]:
        if usuario_logado.papel == PapelEnum.FUNCIONARIO:
            raise PermissionError('Sem permissao para ver relatorios.')

        inicio, final = self._obter_intervalo_filtro_datas(
            FiltroDatas.PERSONALIZADO, data_inicial, data_final
        )
        relatorio = self.venda_repository.listar_produtos_mais_vendidos(inicio, final)

        return relatorio

    def _obter_intervalo_filtro_datas(
        self, filtro_datas: FiltroDatas, inicio_filtro=None, final_filtro=None
    ) -> tuple[datetime, datetime]:
        inicio, final = self._obter_datas_filtro(
            filtro_datas, inicio_filtro, final_filtro
        )

        inicio_utc = datetime.combine(inicio, time.min, tzinfo=FUSO_HORARIO).astimezone(
            timezone.utc
        )
        final_utc = datetime.combine(final, time.min, tzinfo=FUSO_HORARIO).astimezone(
            timezone.utc
        )

        return inicio_utc, final_utc

    @staticmethod
    def _obter_datas_filtro(
        filtro_datas: FiltroDatas, inicio_filtro=None, final_filtro=None
    ) -> tuple[date, date]:
        hoje = datetime.now(FUSO_HORARIO).date()
        inicio_mes = hoje.replace(day=1)
        inicio_ano = date(hoje.year, 1, 1)

        match filtro_datas:
            case FiltroDatas.HOJE:
                inicio = hoje
                final = hoje + timedelta(days=1)

            case FiltroDatas.ONTEM:
                inicio = hoje - timedelta(days=1)
                final = hoje

            case FiltroDatas.ULTIMOS_7_DIAS:
                inicio = hoje - timedelta(days=6)
                final = hoje + timedelta(days=1)

            case FiltroDatas.ULTIMOS_30_DIAS:
                inicio = hoje - timedelta(days=29)
                final = hoje + timedelta(days=1)

            case FiltroDatas.MES_ATUAL:
                inicio = inicio_mes
                final = inicio_mes.replace(
                    year=inicio_mes.year + (inicio_mes.month == MES_DEZEMBRO),
                    month=inicio_mes.month % 12 + 1,
                )

            case FiltroDatas.MES_ANTERIOR:
                final = inicio_mes
                inicio = (inicio_mes - timedelta(days=1)).replace(day=1)

            case FiltroDatas.ANO_ATUAL:
                inicio = inicio_ano
                final = date(hoje.year + 1, 1, 1)

            case FiltroDatas.ANO_ANTERIOR:
                final = inicio_ano
                inicio = date(hoje.year - 1, 1, 1)

            case FiltroDatas.PERSONALIZADO:
                if inicio_filtro is None or final_filtro is None:
                    raise ValueError('As duas datas devem estar preenchidas.')

                if final_filtro < inicio_filtro:
                    raise ValueError(
                        'A data final nao pode ser anterior a data inicial.'
                    )

                inicio = inicio_filtro
                final = final_filtro + timedelta(days=1)

            case _:
                raise ValueError(f'Filtro de data não suportado: {filtro_datas}')

        return inicio, final
