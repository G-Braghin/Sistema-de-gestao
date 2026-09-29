from datetime import datetime, timezone

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
from src.utils.validacoes import verificar_id

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
    ) -> None:
        verificar_id(id_venda),

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

    def listar_resumo(
        self, usuario_logado: Usuario, status_venda: StatusVenda = StatusVenda.CONCLUIDO
    ) -> list[VendaResumo]:
        if usuario_logado.papel == PapelUsuario.FUNCIONARIO:
            raise PermissionError("Sem permissao para ver lista vendas.")

        conn = self.conexao.get_connection()
        with conn:
            vendas = self.venda_repository.listar_resumo(status_venda)

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
