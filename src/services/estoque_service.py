from src.entities.enums.papel_usuario import PapelUsuario
from src.entities.enums.tipo_movimentacao import TipoMovimentacao
from src.entities.movimentacao_estoque import MovimentacaoEstoque
from src.entities.produto import Produto
from src.entities.usuario import Usuario
from src.repositories.movimentacao_repository import MovimentacaoRepository
from src.repositories.produto_repository import ProdutoRepository

PRODUTO_NAO_ENCONTRADO = "Produto nao encontrado!"


class EstoqueService:
    def __init__(
        self,
        produto_repository: ProdutoRepository,
        movimentacao_repository: MovimentacaoRepository,
    ):
        self.produto_repository = produto_repository
        self.movimentacao_repository = movimentacao_repository

    def dar_entrada(
        self, usuario_logado: Usuario, id_produto: int, entrada_estoque: int
    ) -> Produto:
        if entrada_estoque <= 0:
            raise ValueError("Quantidade deve ser maior que 0")

        produto = self.produto_repository.buscar_por_id(id_produto)
        if not produto:
            raise ValueError(PRODUTO_NAO_ENCONTRADO)

        produto.quantidade_estoque += entrada_estoque
        self.produto_repository.atualizar(produto)

        movimentacao = MovimentacaoEstoque(
            id_produto=id_produto,
            id_usuario=usuario_logado.id_usuario,
            tipo=TipoMovimentacao.ENTRADA,
            quantidade=entrada_estoque,
        )
        self.movimentacao_repository.criar(movimentacao)

        return produto

    def dar_saida(
        self, usuario_logado: Usuario, id_produto: int, saida_estoque: int
    ) -> Produto:

        if saida_estoque <= 0:
            raise ValueError("Quantidade deve ser maior que 0")

        produto = self.produto_repository.buscar_por_id(id_produto)
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
        return self.movimentacao_repository.listar()

    def validar_disponibilidade(
        self, id_produto: int, quantidade_desejada: int
    ) -> bool:
        if quantidade_desejada <= 0:
            raise ValueError("Quantidade deve ser maior que 0.")

        produto = self.produto_repository.buscar_por_id(id_produto)
        if not produto:
            raise ValueError(PRODUTO_NAO_ENCONTRADO)

        return produto.quantidade_estoque >= quantidade_desejada
