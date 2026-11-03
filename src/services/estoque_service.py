from src.entities.dtos.relatorio_estoque_resumo import RelatorioEstoqueResumo
from src.enums import MotivoMovimentacao, PapelEnum, TipoMovimentacao
from src.models import Movimentacao, Produto, Usuario
from src.repositories.movimentacao_repository import MovimentacaoRepository
from src.repositories.produto_repository import ProdutoRepository
from src.utils.validacoes import verificar_id

PRODUTO_NAO_ENCONTRADO = 'Produto nao encontrado!'
ID_INVALIDO = 'ID de produto invalido.'


class EstoqueService:
    def __init__(
        self,
        produto_repository: ProdutoRepository,
        movimentacao_repository: MovimentacaoRepository,
    ):
        self.produto_repository = produto_repository
        self.movimentacao_repository = movimentacao_repository

    def dar_entrada(
        self,
        usuario_logado: Usuario,
        id_produto: int,
        entrada_estoque: int,
        motivo: MotivoMovimentacao,
    ) -> Produto:
        if usuario_logado.papel == PapelEnum.FUNCIONARIO:
            raise PermissionError('Sem permissao para mecher no estoque')

        self._verificar_quantidade(entrada_estoque)
        verificar_id(id_produto, ID_INVALIDO)

        produto = self.produto_repository.buscar_por_id_para_atualizar(id_produto)
        if not produto:
            raise ValueError(PRODUTO_NAO_ENCONTRADO)

        produto.quantidade += entrada_estoque
        self.produto_repository.atualizar(produto)

        movimentacao = Movimentacao(
            id_produto=id_produto,
            id_usuario=usuario_logado.id,
            tipo_movimentacao=TipoMovimentacao.ENTRADA,
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
        if usuario_logado.papel == PapelEnum.FUNCIONARIO:
            raise PermissionError('Sem permissao para mecher no estoque')

        self._verificar_quantidade(saida_estoque)
        verificar_id(id_produto, ID_INVALIDO)

        produto = self.produto_repository.buscar_por_id_para_atualizar(id_produto)
        if not produto:
            raise ValueError(PRODUTO_NAO_ENCONTRADO)

        if saida_estoque > produto.quantidade:
            raise ValueError(f'Estoque indisponivel! Disponivel {produto.quantidade}.')

        produto.quantidade -= saida_estoque
        self.produto_repository.atualizar(produto)

        movimentacao = Movimentacao(
            id_produto=id_produto,
            id_usuario=usuario_logado.id,
            tipo_movimentacao=TipoMovimentacao.SAIDA,
            quantidade=saida_estoque,
            motivo=motivo,
        )
        self.movimentacao_repository.criar(movimentacao)

        return produto

    def listar_movimentacoes(self, usuario_logado: Usuario) -> list[Movimentacao]:
        if usuario_logado.papel not in {
            PapelEnum.ADMIN,
            PapelEnum.GERENTE,
        }:
            raise PermissionError(
                'Você não tem permissão para ver o histórico de movimentações.'
            )
        return self.movimentacao_repository.listar()

    def validar_disponibilidade(
        self, id_produto: int, quantidade_desejada: int
    ) -> bool:
        self._verificar_quantidade(quantidade_desejada)
        verificar_id(id_produto, ID_INVALIDO)

        produto = self.produto_repository.buscar_por_id(id_produto)
        if not produto:
            raise ValueError(PRODUTO_NAO_ENCONTRADO)

        return produto.quantidade >= quantidade_desejada

    @staticmethod
    def _verificar_quantidade(quantidade: int) -> None:
        if not isinstance(quantidade, int) or isinstance(quantidade, bool):
            raise TypeError('Quantidade deve ser um numero inteiro.')

        if quantidade <= 0:
            raise ValueError('Quantidade deve ser maior que 0.')

    def relatorio_estoque(self, usuario_logado: Usuario) -> RelatorioEstoqueResumo:
        if usuario_logado.papel == PapelEnum.FUNCIONARIO:
            raise PermissionError(
                'Você não tem permissão para ver o relatorio de estoque.'
            )
        produtos = self.produto_repository.listar()

        total = len(produtos)
        total_quantidade = 0
        total_zero = 0

        for produto in produtos:
            total_quantidade += produto.quantidade
            if produto.quantidade == 0:
                total_zero += 1

        return RelatorioEstoqueResumo(
            produtos=produtos,
            quantidade_produtos_cadastrados=total,
            total_unidades_estoque=total_quantidade,
            quantidade_produtos_sem_estoque=total_zero,
        )

    def relatorio_estoque_baixo(
        self, usuario_logado: Usuario, limite: int
    ) -> list[Produto]:
        if usuario_logado.papel == PapelEnum.FUNCIONARIO:
            raise PermissionError(
                'Você não tem permissão para ver o relatorio de estoque.'
            )

        if not isinstance(limite, int) or isinstance(limite, bool):
            raise TypeError('Limite deve ser um numero inteiro.')

        if limite < 0:
            raise ValueError('Limite nao pode ser menor que 0.')

        produtos = self.produto_repository.listar()
        produtos_limite = []
        for produto in produtos:
            if produto.quantidade <= limite:
                produtos_limite.append(produto)

        produtos_limite.sort(key=lambda produto: (produto.quantidade, produto.nome))

        return produtos_limite
