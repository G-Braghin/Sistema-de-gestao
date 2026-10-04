from datetime import date, datetime, timedelta, timezone

from src.database.conexao import Conexao
from src.entities.enums.papel_usuario import PapelUsuario
from src.entities.enums.status_venda import StatusVenda
from src.entities.usuario import Usuario
from src.entities.venda import Venda
from src.entities.venda_item import VendaItem
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.produto_repository import ProdutoRepository
from src.repositories.venda_repository import VendaRepository
from src.services.estoque_service import EstoqueService
from src.utils.filtro_datas import FiltroDatas
from src.utils.validacoes import verificar_id

from ..entities.dtos.relatorio_venda_resumo import RelatorioVendaResumo
from ..entities.dtos.venda_resumo import VendaResumo


class VendaService:
    def __init__(
        self,
        conexao: Conexao,
        venda_repository: VendaRepository,
        produto_repository: ProdutoRepository,
        cliente_repository: ClienteRepository,
        estoque_service: EstoqueService,
    ):
        self.conexao = conexao
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
        verificar_id(id_cliente, "ID de cliente invalido.")
        conn = self.conexao.get_connection()
        with conn:
            cliente = self.cliente_repository.buscar_por_id(id_cliente)
            if not cliente:
                raise ValueError("Cliente nao encontrado.")

            if cliente.ativo == False:
                raise ValueError("Cliente nao pode estar desativado.")

            venda_itens = self._criar_itens_venda(itens)

            total = sum(item.preco_unitario * item.quantidade for item in venda_itens)

            venda = Venda(
                id_cliente=id_cliente,
                id_usuario=usuario_logado.id_usuario,
                itens=venda_itens,
                preco_total=total,
                status=StatusVenda.CONCLUIDO,
            )

            self.venda_repository.criar(venda)

            for item in venda_itens:
                self.estoque_service.registrar_saida(
                    usuario_logado=usuario_logado,
                    id_produto=item.id_produto,
                    saida_estoque=item.quantidade,
                    id_venda=item.id_venda,
                )

        return venda

    def _criar_itens_venda(self, itens: list[dict]) -> list[VendaItem]:
        if not itens:
            raise ValueError("Ao menos deve ter um item.")

        return [self._criar_item_venda(item) for item in itens]

    def _criar_item_venda(self, item: dict) -> VendaItem:

        if "id_produto" not in item:
            raise ValueError("O produto deve ter um ID obrigatorio")

        if "quantidade" not in item:
            raise ValueError("O produto deve ter uma quantidade.")

        quantidade = item["quantidade"]
        id_produto = item["id_produto"]

        if not isinstance(quantidade, int) or isinstance(quantidade, bool):
            raise TypeError("Quantidade deve ser um numero inteiro.")

        if quantidade <= 0:
            raise ValueError("Quantiade de ser maior que 0.")

        verificar_id(id_produto)

        produto = self.produto_repository.buscar_por_id(id_produto)
        if not produto:
            raise ValueError(f"Produto de id: {id_produto} nao encontrado")

        if not self.estoque_service.validar_disponibilidade(id_produto, quantidade):
            raise ValueError(
                f"Estoque insuficiente para o produto: {produto.nome} "
                f"Disponivel: {produto.quantidade_estoque}"
            )

        return VendaItem(
            id_produto=id_produto,
            nome_produto=produto.nome,
            quantidade=quantidade,
            preco_unitario=produto.preco,
        )

    def cancelar_venda(
        self,
        usuario_logado: Usuario,
        id_venda: int,
    ) -> None | Venda:
        verificar_id(id_venda)

        if usuario_logado.papel == PapelUsuario.FUNCIONARIO:
            raise PermissionError("Sem permissao para cancelar vendas.")

        conn = self.conexao.get_connection()
        with conn:

            self.venda_repository.cancelar_venda(
                id_venda=id_venda,
                data_cancelamento=datetime.now(timezone.utc),
                id_usuario_cancelamento=usuario_logado.id_usuario,
            )
            venda = self.venda_repository.buscar_por_id(id_venda)
            for item in venda.itens:
                self.estoque_service.registrar_entrada(
                    usuario_logado=usuario_logado,
                    id_produto=item.id_produto,
                    entrada_estoque=item.quantidade,
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
        if usuario_logado.papel == PapelUsuario.FUNCIONARIO:
            raise PermissionError("Sem permissao para ver lista vendas.")

        if filtro_data is None:
            filtro_data = FiltroDatas.MES_ATUAL

        data_inicial, data_final = self._obter_intervalo_filtro_datas(
            filtro_data, inicio_filtro, final_filtro
        )

        conn = self.conexao.get_connection()
        with conn:
            vendas = self.venda_repository.listar_resumo(
                data_inicial, data_final, status_venda
            )

        return vendas

    def listar_venda_itens(self, usuario_logado: Usuario, id_venda: int):
        verificar_id(id_venda)
        if usuario_logado.papel == PapelUsuario.FUNCIONARIO:
            raise PermissionError("Sem Permissao para ver venda de itens.")

        conn = self.conexao.get_connection()
        with conn:
            vendas = self.venda_repository.buscar_por_id(id_venda)
            if vendas is None:
                raise ValueError("ID nao encontrado.")

            return vendas

    def _obter_intervalo_filtro_datas(
        self, filtro_datas: FiltroDatas, inicio_filtro=None, final_filtro=None
    ) -> tuple[date, date]:
        hoje = datetime.now(timezone.utc).date()

        if filtro_datas == FiltroDatas.HOJE:
            amanha = hoje + timedelta(days=1)

            return hoje, amanha

        elif filtro_datas == FiltroDatas.ONTEM:
            ontem = hoje - timedelta(days=1)

            return ontem, hoje

        elif filtro_datas == FiltroDatas.ULTIMOS_7_DIAS:
            amanha = hoje + timedelta(days=1)
            sete_dias_atras = hoje - timedelta(days=6)

            return sete_dias_atras, amanha

        elif filtro_datas == FiltroDatas.ULTIMOS_30_DIAS:
            amanha = hoje + timedelta(days=1)
            trinta_dias_atras = hoje - timedelta(days=29)

            return trinta_dias_atras, amanha

        elif filtro_datas == FiltroDatas.MES_ATUAL:
            inicio_mes_atual = hoje.replace(day=1)
            if hoje.month == 12:
                inicio_proximo_mes = date(hoje.year + 1, 1, 1)
            else:
                inicio_proximo_mes = date(hoje.year, hoje.month + 1, 1)

            return inicio_mes_atual, inicio_proximo_mes

        elif filtro_datas == FiltroDatas.MES_ANTERIOR:
            inicio_mes_atual = hoje.replace(day=1)
            final_mes_anterior = inicio_mes_atual - timedelta(days=1)
            inicio_mes_anterior = final_mes_anterior.replace(day=1)

            return inicio_mes_anterior, inicio_mes_atual

        elif filtro_datas == FiltroDatas.ANO_ATUAL:
            inicio_proximo_ano = date(hoje.year + 1, 1, 1)
            inicio_ano_atual = date(hoje.year, 1, 1)

            return inicio_ano_atual, inicio_proximo_ano

        elif filtro_datas == FiltroDatas.ANO_ANTERIOR:
            inicio_ano_atual = date(hoje.year, 1, 1)
            inicio_ano_anterior = date(hoje.year - 1, 1, 1)

            return inicio_ano_anterior, inicio_ano_atual

        elif filtro_datas == FiltroDatas.PERSONALIZADO:
            if inicio_filtro == None or final_filtro == None:
                raise ValueError("As duas datas devem estar preenchidas.")

            if final_filtro < inicio_filtro:
                raise ValueError("A data final nao pode ser anterior a data inicial.")

            return inicio_filtro, final_filtro + timedelta(days=1)

        raise ValueError(f"Filtro de data não suportado: {filtro_datas}")

    def criar_resumo_relatorio(
        self, usuario_logado: Usuario, data_inicial: date, data_final: date
    ):
        conn = self.conexao.get_connection()
        if usuario_logado.papel == PapelUsuario.FUNCIONARIO:
            raise PermissionError("Sem permissao para ver relatorios.")

        with conn:
            inicio, final = self._obter_intervalo_filtro_datas(
                FiltroDatas.PERSONALIZADO, data_inicial, data_final
            )

            vendas = self.venda_repository.listar_resumo(
                inicio, final, StatusVenda.CONCLUIDO
            )
            if not vendas:
                return None

            num_vendas_concluidas = 0
            total_periodo = 0

            for venda in vendas:
                total_periodo += venda.valor_total
                num_vendas_concluidas += 1

            ticket_medio = total_periodo / num_vendas_concluidas

            relatorio = RelatorioVendaResumo(
                data_inicial=data_inicial,
                data_final=data_final,
                vendas_concluidas=num_vendas_concluidas,
                total_periodo=total_periodo,
                ticket_medio=ticket_medio,
            )

        return relatorio
