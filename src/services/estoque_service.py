from src.database.conexao import Conexao
from src.entities.enums.motivo_movimentacao import MotivoMovimentacao
from src.entities.enums.papel_usuario import PapelUsuario
from src.entities.enums.tipo_movimentacao import TipoMovimentacao
from src.entities.movimentacao_estoque import MovimentacaoEstoque
from src.entities.produto import Produto
from src.entities.usuario import Usuario
from src.repositories.movimentacao_repository import MovimentacaoRepository
from src.repositories.produto_repository import ProdutoRepository
from src.utils.validacoes import verificar_id
from src.entities.dtos.relatorio_estoque_resumo import RelatorioEstoqueResumo

PRODUTO_NAO_ENCONTRADO = "Produto nao encontrado!"
ID_INVALIDO = "ID de produto invalido."


class EstoqueService:
    def __init__(
        self,
        produto_repository: ProdutoRepository,
        movimentacao_repository: MovimentacaoRepository,
        conexao: Conexao,
    ):
        self.produto_repository = produto_repository
        self.movimentacao_repository = movimentacao_repository
        self.conexao = conexao

    def dar_entrada(
        self,
        usuario_logado: Usuario,
        id_produto: int,
        entrada_estoque: int,
        motivo: MotivoMovimentacao,
    ) -> Produto:
        if usuario_logado.papel == PapelUsuario.FUNCIONARIO:
            raise PermissionError("Sem permissao para mecher no estoque")

        self._verificar_quantidade(entrada_estoque)
        verificar_id(id_produto, ID_INVALIDO)

        conn = self.conexao.get_connection()
        with conn:
            produto = self.produto_repository.buscar_por_id_para_atualizar(id_produto)
            if not produto:
                raise ValueError(PRODUTO_NAO_ENCONTRADO)

            produto.quantidade_estoque += entrada_estoque
            self.produto_repository.atualizar(produto)

            movimentacao = MovimentacaoEstoque(
                id_produto=id_produto,
                id_usuario=usuario_logado.id_usuario,
                tipo=TipoMovimentacao.ENTRADA,
                quantidade=entrada_estoque,
                motivo=motivo,
            )
            self.movimentacao_repository.criar(movimentacao)

        return produto

    def dar_saida(
        self,
        usuario_logado: Usuario,
        id_produto: int,
        saida_estoque: int,
        motivo: MotivoMovimentacao,
    ) -> Produto:
        if usuario_logado.papel == PapelUsuario.FUNCIONARIO:
            raise PermissionError("Sem permissao para mecher no estoque")

        self._verificar_quantidade(saida_estoque)
        verificar_id(id_produto, ID_INVALIDO)

        conn = self.conexao.get_connection()
        with conn:
            produto = self.produto_repository.buscar_por_id_para_atualizar(id_produto)
            if not produto:
                raise ValueError(PRODUTO_NAO_ENCONTRADO)

            if saida_estoque > produto.quantidade_estoque:
                raise ValueError(
                    f"Estoque indisponivel! Disponivel {produto.quantidade_estoque}."
                )

            produto.quantidade_estoque -= saida_estoque
            self.produto_repository.atualizar(produto)

            movimentacao = MovimentacaoEstoque(
                id_produto=id_produto,
                id_usuario=usuario_logado.id_usuario,
                tipo=TipoMovimentacao.SAIDA,
                quantidade=saida_estoque,
                motivo=motivo,
            )
            self.movimentacao_repository.criar(movimentacao)

        return produto

    def listar_movimentacoes(
        self, usuario_logado: Usuario
    ) -> list[MovimentacaoEstoque]:
        if usuario_logado.papel not in (
            PapelUsuario.ADMINISTRADOR,
            PapelUsuario.GERENTE,
        ):
            raise PermissionError(
                "Você não tem permissão para ver o histórico de movimentações."
            )
        conn = self.conexao.get_connection()
        with conn:
            return self.movimentacao_repository.listar()

    def validar_disponibilidade(
        self, id_produto: int, quantidade_desejada: int
    ) -> bool:
        self._verificar_quantidade(quantidade_desejada)
        verificar_id(id_produto, ID_INVALIDO)

        produto = self.produto_repository.buscar_por_id(id_produto)
        if not produto:
            raise ValueError(PRODUTO_NAO_ENCONTRADO)

        return produto.quantidade_estoque >= quantidade_desejada

    def _verificar_quantidade(self, quantidade: int) -> None:
        if not isinstance(quantidade, int) or isinstance(quantidade, bool):
            raise TypeError("Quantidade deve ser um numero inteiro.")

        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que 0.")

    # este metodo deve ser usado por quem faz a transacao com o banco de dados
    def registrar_saida(
        self,
        usuario_logado: Usuario,
        id_produto: int,
        saida_estoque: int,
        id_venda: int,
    ) -> Produto:
        self._verificar_quantidade(saida_estoque)
        verificar_id(id_produto, ID_INVALIDO)

        produto = self.produto_repository.buscar_por_id_para_atualizar(id_produto)
        if not produto:
            raise ValueError(PRODUTO_NAO_ENCONTRADO)

        if saida_estoque > produto.quantidade_estoque:
            raise ValueError(
                f"Estoque indisponivel! Disponivel {produto.quantidade_estoque}."
            )

        produto.quantidade_estoque -= saida_estoque
        self.produto_repository.atualizar(produto)

        movimentacao = MovimentacaoEstoque(
            id_produto=id_produto,
            id_usuario=usuario_logado.id_usuario,
            tipo=TipoMovimentacao.SAIDA,
            quantidade=saida_estoque,
            motivo=MotivoMovimentacao.VENDA,
            id_venda=id_venda,
        )
        self.movimentacao_repository.criar(movimentacao)

        return produto

    def registrar_entrada(
        self,
        usuario_logado: Usuario,
        id_produto: int,
        entrada_estoque: int,
        id_venda: int,
    ) -> Produto:
        self._verificar_quantidade(entrada_estoque)
        verificar_id(id_produto, ID_INVALIDO)

        produto = self.produto_repository.buscar_por_id_para_atualizar(id_produto)
        if not produto:
            raise ValueError(PRODUTO_NAO_ENCONTRADO)

        produto.quantidade_estoque += entrada_estoque
        self.produto_repository.atualizar(produto)

        movimentacao = MovimentacaoEstoque(
            id_produto=id_produto,
            id_usuario=usuario_logado.id_usuario,
            tipo=TipoMovimentacao.ENTRADA,
            quantidade=entrada_estoque,
            motivo=MotivoMovimentacao.CANCELAMENTO_VENDA,
            id_venda=id_venda,
        )
        self.movimentacao_repository.criar(movimentacao)

        return produto

    def relatorio_estoque(self, usuario_logado: Usuario):
        if usuario_logado.papel == PapelUsuario.FUNCIONARIO:
            raise PermissionError(
                "Você não tem permissão para ver o relatorio de estoque."
            )
        conn = self.conexao.get_connection()

        with conn:
            produtos = self.produto_repository.listar()

            total = len(produtos)
            total_quantidade = 0
            total_zero = 0

            for produto in produtos:
                total_quantidade += produto.quantidade_estoque
                if produto.quantidade_estoque == 0:
                    total_zero += 1

            relatorio = RelatorioEstoqueResumo(
                produtos=produtos,
                quantidade_produtos_cadastrados=total,
                total_unidades_estoque=total_quantidade,
                quantidade_produtos_sem_estoque=total_zero,
            )

        return relatorio

    def relatorio_estoque_baixo(
        self, usuario_logado: Usuario, limite: int
    ) -> list[Produto]:
        if usuario_logado.papel == PapelUsuario.FUNCIONARIO:
            raise PermissionError(
                "Você não tem permissão para ver o relatorio de estoque."
            )

        if not isinstance(limite, int) or isinstance(limite, bool):
            raise TypeError("Limite deve ser um numero inteiro.")

        if limite < 0:
            raise ValueError("Limite nao pode ser menor que 0.")

        conn = self.conexao.get_connection()
        with conn:
            produtos = self.produto_repository.listar()
            produtos_limite = []
            for produto in produtos:
                if produto.quantidade_estoque <= limite:
                    produtos_limite.append(produto)

        produtos_limite.sort(
            key=lambda produto: (produto.quantidade_estoque, produto.nome)
        )

        return produtos_limite
