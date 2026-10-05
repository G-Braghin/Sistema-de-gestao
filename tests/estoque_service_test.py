from decimal import Decimal
from unittest.mock import MagicMock, Mock

import pytest

from src.entities.dtos.relatorio_estoque_resumo import RelatorioEstoqueResumo
from src.entities.enums.motivo_movimentacao import MotivoMovimentacao
from src.entities.enums.papel_usuario import PapelUsuario
from src.entities.enums.tipo_movimentacao import TipoMovimentacao
from src.entities.movimentacao_estoque import MovimentacaoEstoque
from src.entities.produto import Produto
from src.entities.usuario import Usuario
from src.services.estoque_service import EstoqueService


@pytest.fixture
def produto_repository():
    return Mock()


@pytest.fixture
def movimentacao_repository():
    return Mock()


@pytest.fixture
def conexao():
    conexao = Mock()
    conexao.get_connection.return_value = MagicMock()
    return conexao


@pytest.fixture
def service(produto_repository, movimentacao_repository, conexao):
    return EstoqueService(
        produto_repository,
        movimentacao_repository,
        conexao
    )


@pytest.fixture
def usuario():
    return Usuario(
        id_usuario=1,
        nome="TESTE_USUARIO",
        senha_hash="teste_hash",
        papel=PapelUsuario.GERENTE,
        ativo=True
    )


@pytest.fixture
def produto():
    return Produto(
        id_produto=1,
        nome="TECLADO",
        marca="LOGITECH",
        preco=Decimal("150.00"),
        quantidade_estoque=10
    )


@pytest.mark.parametrize('papel', [PapelUsuario.ADMINISTRADOR, PapelUsuario.GERENTE])
def test_relatorio_estoque_calcula_totais(
    service, produto_repository, movimentacao_repository, conexao, usuario, papel
):
    usuario.papel = papel
    produtos = [
        Produto('TECLADO', 'LOGITECH', Decimal('150.00'), 5, 1),
        Produto('MOUSE', 'LOGITECH', Decimal('25.00'), 10, 2),
        Produto('CABO', 'INTELBRAS', Decimal('15.00'), 0, 3),
    ]
    produto_repository.listar.return_value = produtos

    relatorio = service.relatorio_estoque(usuario)

    assert isinstance(relatorio, RelatorioEstoqueResumo)
    assert relatorio.produtos == produtos
    assert relatorio.quantidade_produtos_cadastrados == 3
    assert relatorio.total_unidades_estoque == 15
    assert relatorio.quantidade_produtos_sem_estoque == 1
    assert [produto.quantidade_estoque for produto in produtos] == [5, 10, 0]
    produto_repository.listar.assert_called_once_with()
    produto_repository.atualizar.assert_not_called()
    movimentacao_repository.criar.assert_not_called()
    conn = conexao.get_connection.return_value
    conn.__enter__.assert_called_once()
    conn.__exit__.assert_called_once_with(None, None, None)


def test_relatorio_estoque_sem_produtos(service, produto_repository, usuario):
    produto_repository.listar.return_value = []

    relatorio = service.relatorio_estoque(usuario)

    assert isinstance(relatorio, RelatorioEstoqueResumo)
    assert relatorio.produtos == []
    assert relatorio.quantidade_produtos_cadastrados == 0
    assert relatorio.total_unidades_estoque == 0
    assert relatorio.quantidade_produtos_sem_estoque == 0


def test_relatorio_estoque_com_todos_os_produtos_zerados(
    service, produto_repository, usuario
):
    produtos = [
        Produto('TECLADO', 'LOGITECH', Decimal('150.00'), 0, 1),
        Produto('MOUSE', 'LOGITECH', Decimal('25.00'), 0, 2),
    ]
    produto_repository.listar.return_value = produtos

    relatorio = service.relatorio_estoque(usuario)

    assert relatorio.produtos == produtos
    assert relatorio.quantidade_produtos_cadastrados == 2
    assert relatorio.total_unidades_estoque == 0
    assert relatorio.quantidade_produtos_sem_estoque == 2


def test_relatorio_estoque_sem_permissao(
    service, produto_repository, conexao, usuario
):
    usuario.papel = PapelUsuario.FUNCIONARIO

    with pytest.raises(PermissionError, match='Você não tem permissão'):
        service.relatorio_estoque(usuario)

    conexao.get_connection.assert_not_called()
    produto_repository.listar.assert_not_called()


def test_relatorio_estoque_propaga_erro_da_consulta(
    service, produto_repository, conexao, usuario
):
    erro = RuntimeError('Erro ao consultar produtos')
    produto_repository.listar.side_effect = erro

    with pytest.raises(RuntimeError, match='Erro ao consultar produtos'):
        service.relatorio_estoque(usuario)

    conn = conexao.get_connection.return_value
    conn.__exit__.assert_called_once()
    assert conn.__exit__.call_args.args[0] is RuntimeError
    assert conn.__exit__.call_args.args[1] is erro


@pytest.mark.parametrize('papel', [PapelUsuario.ADMINISTRADOR, PapelUsuario.GERENTE])
def test_relatorio_estoque_baixo_filtra_e_ordena(
    service, produto_repository, movimentacao_repository, conexao, usuario, papel
):
    usuario.papel = papel
    produtos = [
        Produto('TECLADO', 'LOGITECH', Decimal('150.00'), 5, 1),
        Produto('ADAPTADOR', 'INTELBRAS', Decimal('20.00'), 6, 2),
        Produto('CABO', 'INTELBRAS', Decimal('15.00'), 5, 3),
        Produto('MOUSE', 'LOGITECH', Decimal('25.00'), 0, 4),
        Produto('PILHA', 'ELGIN', Decimal('5.00'), 2, 5),
    ]
    produto_repository.listar.return_value = produtos

    resultado = service.relatorio_estoque_baixo(usuario, 5)

    assert resultado == [produtos[3], produtos[4], produtos[2], produtos[0]]
    assert [produto.id_produto for produto in produtos] == [1, 2, 3, 4, 5]
    assert [produto.quantidade_estoque for produto in produtos] == [5, 6, 5, 0, 2]
    produto_repository.listar.assert_called_once_with()
    produto_repository.atualizar.assert_not_called()
    movimentacao_repository.criar.assert_not_called()
    conn = conexao.get_connection.return_value
    conn.__enter__.assert_called_once()
    conn.__exit__.assert_called_once_with(None, None, None)


def test_relatorio_estoque_baixo_com_limite_zero(
    service, produto_repository, usuario
):
    produto_zerado = Produto('CABO', 'INTELBRAS', Decimal('15.00'), 0, 1)
    produto_com_estoque = Produto('MOUSE', 'LOGITECH', Decimal('25.00'), 1, 2)
    produto_repository.listar.return_value = [produto_com_estoque, produto_zerado]

    resultado = service.relatorio_estoque_baixo(usuario, 0)

    assert resultado == [produto_zerado]


def test_relatorio_estoque_baixo_sem_produtos(service, produto_repository, usuario):
    produto_repository.listar.return_value = []

    resultado = service.relatorio_estoque_baixo(usuario, 5)

    assert resultado == []


def test_relatorio_estoque_baixo_sem_produtos_dentro_do_limite(
    service, produto_repository, usuario, produto
):
    produto_repository.listar.return_value = [produto]

    resultado = service.relatorio_estoque_baixo(usuario, 5)

    assert resultado == []


def test_relatorio_estoque_baixo_com_limite_negativo(
    service, produto_repository, conexao, usuario
):
    with pytest.raises(ValueError, match='Limite nao pode ser menor que 0'):
        service.relatorio_estoque_baixo(usuario, -1)

    conexao.get_connection.assert_not_called()
    produto_repository.listar.assert_not_called()


@pytest.mark.parametrize('limite', ['5', 5.0, None, True, False])
def test_relatorio_estoque_baixo_com_tipo_de_limite_invalido(
    service, produto_repository, conexao, usuario, limite
):
    with pytest.raises(TypeError, match='Limite deve ser um numero inteiro'):
        service.relatorio_estoque_baixo(usuario, limite)

    conexao.get_connection.assert_not_called()
    produto_repository.listar.assert_not_called()


def test_relatorio_estoque_baixo_sem_permissao(
    service, produto_repository, conexao, usuario
):
    usuario.papel = PapelUsuario.FUNCIONARIO

    with pytest.raises(PermissionError, match='Você não tem permissão'):
        service.relatorio_estoque_baixo(usuario, 5)

    conexao.get_connection.assert_not_called()
    produto_repository.listar.assert_not_called()


def test_relatorio_estoque_baixo_propaga_erro_da_consulta(
    service, produto_repository, conexao, usuario
):
    erro = RuntimeError('Erro ao consultar produtos')
    produto_repository.listar.side_effect = erro

    with pytest.raises(RuntimeError, match='Erro ao consultar produtos'):
        service.relatorio_estoque_baixo(usuario, 5)

    conn = conexao.get_connection.return_value
    conn.__exit__.assert_called_once()
    assert conn.__exit__.call_args.args[0] is RuntimeError
    assert conn.__exit__.call_args.args[1] is erro


@pytest.mark.parametrize('operacao', ['dar_entrada', 'dar_saida'])
def test_funcionario_nao_pode_alterar_estoque(
    service, produto_repository, movimentacao_repository, conexao, usuario, operacao
):
    usuario.papel = PapelUsuario.FUNCIONARIO

    with pytest.raises(PermissionError, match='Sem permissao'):
        getattr(service, operacao)(usuario, 1, 5, MotivoMovimentacao.AJUSTE)

    conexao.get_connection.assert_not_called()
    produto_repository.buscar_por_id.assert_not_called()
    produto_repository.atualizar.assert_not_called()
    movimentacao_repository.criar.assert_not_called()


def test_dar_entrada_propaga_erro_da_movimentacao(
    service, produto_repository, movimentacao_repository, conexao, usuario, produto
):
    conn = conexao.get_connection.return_value
    produto_repository.buscar_por_id.return_value = produto
    erro = RuntimeError("Erro ao salvar movimentacao")
    movimentacao_repository.criar.side_effect = erro

    with pytest.raises(RuntimeError, match="Erro ao salvar movimentacao"):
        service.dar_entrada(usuario, produto.id_produto, 5, MotivoMovimentacao.REPOSICAO)

    produto_repository.atualizar.assert_called_once_with(produto)
    conn.__enter__.assert_called_once()
    conn.__exit__.assert_called_once()
    assert conn.__exit__.call_args.args[0] is RuntimeError
    assert conn.__exit__.call_args.args[1] is erro


def test_dar_saida_propaga_erro_da_movimentacao(
    service, produto_repository, movimentacao_repository, conexao, usuario, produto
):
    conn = conexao.get_connection.return_value
    produto_repository.buscar_por_id.return_value = produto
    erro = RuntimeError("Erro ao salvar movimentacao")
    movimentacao_repository.criar.side_effect = erro

    with pytest.raises(RuntimeError, match="Erro ao salvar movimentacao"):
        service.dar_saida(usuario, produto.id_produto, 4, MotivoMovimentacao.AJUSTE)

    produto_repository.atualizar.assert_called_once_with(produto)
    conn.__enter__.assert_called_once()
    conn.__exit__.assert_called_once()
    assert conn.__exit__.call_args.args[0] is RuntimeError
    assert conn.__exit__.call_args.args[1] is erro


def test_dar_entrada_com_quantidade_valida(
    service,
    produto_repository,
    movimentacao_repository,
    usuario,
    produto
):
    produto_repository.buscar_por_id.return_value = produto

    movimentacao_repository.criar.return_value = None

    resultado = service.dar_entrada(
        usuario_logado=usuario,
        id_produto=1,
        entrada_estoque=5,
        motivo=MotivoMovimentacao.REPOSICAO
    )

    assert resultado == produto
    assert produto.quantidade_estoque == 15

    produto_repository.buscar_por_id.assert_called_once_with(1)
    produto_repository.atualizar.assert_called_once_with(produto)

    movimentacao_repository.criar.assert_called_once()

    movimentacao = movimentacao_repository.criar.call_args.args[0]

    assert isinstance(movimentacao, MovimentacaoEstoque)
    assert movimentacao.id_produto == 1
    assert movimentacao.id_usuario == usuario.id_usuario
    assert movimentacao.motivo == MotivoMovimentacao.REPOSICAO
    assert movimentacao.id_venda is None
    assert movimentacao.tipo == TipoMovimentacao.ENTRADA
    assert movimentacao.quantidade == 5


def test_dar_entrada_com_quantidade_zero(
    service,
    produto_repository,
    movimentacao_repository,
    usuario
):
    with pytest.raises(
        ValueError,
        match="Quantidade deve ser maior que 0"
    ):
        service.dar_entrada(
            usuario_logado=usuario,
            id_produto=1,
            entrada_estoque=0,
            motivo=MotivoMovimentacao.REPOSICAO
        )

    produto_repository.buscar_por_id.assert_not_called()
    produto_repository.atualizar.assert_not_called()
    movimentacao_repository.criar.assert_not_called()


def test_dar_entrada_com_quantidade_negativa(
    service,
    produto_repository,
    movimentacao_repository,
    usuario
):
    with pytest.raises(
        ValueError,
        match="Quantidade deve ser maior que 0"
    ):
        service.dar_entrada(
            usuario_logado=usuario,
            id_produto=1,
            entrada_estoque=-5,
            motivo=MotivoMovimentacao.REPOSICAO
        )

    produto_repository.buscar_por_id.assert_not_called()
    produto_repository.atualizar.assert_not_called()
    movimentacao_repository.criar.assert_not_called()


def test_dar_entrada_com_produto_inexistente(
    service,
    produto_repository,
    movimentacao_repository,
    usuario
):
    produto_repository.buscar_por_id.return_value = None

    with pytest.raises(
        ValueError,
        match="Produto nao encontrado"
    ):
        service.dar_entrada(
            usuario_logado=usuario,
            id_produto=999999,
            entrada_estoque=5,
            motivo=MotivoMovimentacao.REPOSICAO
        )

    produto_repository.atualizar.assert_not_called()
    movimentacao_repository.criar.assert_not_called()


def test_dar_saida_com_quantidade_valida(
    service,
    produto_repository,
    movimentacao_repository,
    usuario,
    produto
):
    produto_repository.buscar_por_id.return_value = produto

    movimentacao_repository.criar.return_value = None

    resultado = service.dar_saida(
        usuario_logado=usuario,
        id_produto=1,
        saida_estoque=4,
        motivo=MotivoMovimentacao.AJUSTE
    )

    assert resultado == produto
    assert produto.quantidade_estoque == 6

    produto_repository.buscar_por_id.assert_called_once_with(1)
    produto_repository.atualizar.assert_called_once_with(produto)

    movimentacao_repository.criar.assert_called_once()

    movimentacao = movimentacao_repository.criar.call_args.args[0]

    assert isinstance(movimentacao, MovimentacaoEstoque)
    assert movimentacao.id_produto == 1
    assert movimentacao.id_usuario == usuario.id_usuario
    assert movimentacao.motivo == MotivoMovimentacao.AJUSTE
    assert movimentacao.id_venda is None
    assert movimentacao.tipo == TipoMovimentacao.SAIDA
    assert movimentacao.quantidade == 4


def test_dar_saida_com_quantidade_zero(
    service,
    produto_repository,
    movimentacao_repository,
    usuario
):
    with pytest.raises(
        ValueError,
        match="Quantidade deve ser maior que 0"
    ):
        service.dar_saida(
            usuario_logado=usuario,
            id_produto=1,
            saida_estoque=0,
            motivo=MotivoMovimentacao.AJUSTE
        )

    produto_repository.buscar_por_id.assert_not_called()
    produto_repository.atualizar.assert_not_called()
    movimentacao_repository.criar.assert_not_called()


def test_dar_saida_com_quantidade_negativa(
    service,
    produto_repository,
    movimentacao_repository,
    usuario
):
    with pytest.raises(
        ValueError,
        match="Quantidade deve ser maior que 0"
    ):
        service.dar_saida(
            usuario_logado=usuario,
            id_produto=1,
            saida_estoque=-3,
            motivo=MotivoMovimentacao.AJUSTE
        )

    produto_repository.buscar_por_id.assert_not_called()
    produto_repository.atualizar.assert_not_called()
    movimentacao_repository.criar.assert_not_called()


def test_dar_saida_com_produto_inexistente(
    service,
    produto_repository,
    movimentacao_repository,
    usuario
):
    produto_repository.buscar_por_id.return_value = None

    with pytest.raises(
        ValueError,
        match="Produto nao encontrado"
    ):
        service.dar_saida(
            usuario_logado=usuario,
            id_produto=999999,
            saida_estoque=5,
            motivo=MotivoMovimentacao.AJUSTE
        )

    produto_repository.atualizar.assert_not_called()
    movimentacao_repository.criar.assert_not_called()


def test_dar_saida_com_estoque_insuficiente(
    service,
    produto_repository,
    movimentacao_repository,
    usuario,
    produto
):
    produto_repository.buscar_por_id.return_value = produto

    with pytest.raises(
        ValueError,
        match="Estoque indisponivel"
    ):
        service.dar_saida(
            usuario_logado=usuario,
            id_produto=1,
            saida_estoque=11,
            motivo=MotivoMovimentacao.AJUSTE
        )

    assert produto.quantidade_estoque == 10

    produto_repository.atualizar.assert_not_called()
    movimentacao_repository.criar.assert_not_called()


def test_listar_movimentacoes_com_administrador(
    service,
    movimentacao_repository
):
    usuario = Usuario(
        id_usuario=1,
        nome="TESTE_ADMIN",
        senha_hash="teste_hash",
        papel=PapelUsuario.ADMINISTRADOR,
        ativo=True
    )

    movimentacoes = [
        MovimentacaoEstoque(
            id_produto=1,
            id_usuario=1,
            tipo=TipoMovimentacao.ENTRADA,
            motivo=MotivoMovimentacao.REPOSICAO,
            quantidade=10
        ),
        MovimentacaoEstoque(
            id_produto=1,
            id_usuario=1,
            tipo=TipoMovimentacao.SAIDA,
            motivo=MotivoMovimentacao.AJUSTE,
            quantidade=3
        )
    ]

    movimentacao_repository.listar.return_value = movimentacoes

    resultado = service.listar_movimentacoes(usuario)

    assert resultado == movimentacoes
    movimentacao_repository.listar.assert_called_once()


def test_listar_movimentacoes_com_gerente(
    service,
    movimentacao_repository
):
    usuario = Usuario(
        id_usuario=2,
        nome="TESTE_GERENTE",
        senha_hash="teste_hash",
        papel=PapelUsuario.GERENTE,
        ativo=True
    )

    movimentacoes = [
        MovimentacaoEstoque(
            id_produto=1,
            id_usuario=2,
            tipo=TipoMovimentacao.ENTRADA,
            motivo=MotivoMovimentacao.REPOSICAO,
            quantidade=5
        )
    ]

    movimentacao_repository.listar.return_value = movimentacoes

    resultado = service.listar_movimentacoes(usuario)

    assert resultado == movimentacoes
    movimentacao_repository.listar.assert_called_once()


def test_listar_movimentacoes_sem_permissao(
    service,
    movimentacao_repository,
    usuario
):
    usuario.papel = PapelUsuario.FUNCIONARIO
    with pytest.raises(
        PermissionError,
        match="Você não tem permissão"
    ):
        service.listar_movimentacoes(usuario)

    movimentacao_repository.listar.assert_not_called()


def test_validar_disponibilidade_com_estoque_suficiente(
    service,
    produto_repository,
    produto
):
    produto_repository.buscar_por_id.return_value = produto

    resultado = service.validar_disponibilidade(
        id_produto=1,
        quantidade_desejada=5
    )

    assert resultado is True

    produto_repository.buscar_por_id.assert_called_once_with(1)


def test_validar_disponibilidade_com_estoque_insuficiente(
    service,
    produto_repository,
    produto
):
    produto_repository.buscar_por_id.return_value = produto

    resultado = service.validar_disponibilidade(
        id_produto=1,
        quantidade_desejada=11
    )

    assert resultado is False

    produto_repository.buscar_por_id.assert_called_once_with(1)


def test_validar_disponibilidade_com_quantidade_zero(
    service,
    produto_repository
):
    with pytest.raises(
        ValueError,
        match="Quantidade deve ser maior que 0."
    ):
        service.validar_disponibilidade(
            id_produto=1,
            quantidade_desejada=0
        )

    produto_repository.buscar_por_id.assert_not_called()


def test_validar_disponibilidade_com_quantidade_negativa(
    service,
    produto_repository
):
    with pytest.raises(
        ValueError,
        match="Quantidade deve ser maior que 0."
    ):
        service.validar_disponibilidade(
            id_produto=1,
            quantidade_desejada=-5
        )

    produto_repository.buscar_por_id.assert_not_called()


def test_validar_disponibilidade_com_produto_inexistente(
    service,
    produto_repository
):
    produto_repository.buscar_por_id.return_value = None

    with pytest.raises(
        ValueError,
        match="Produto nao encontrado"
    ):
        service.validar_disponibilidade(
            id_produto=999999,
            quantidade_desejada=5
        )
