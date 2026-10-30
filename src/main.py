from psycopg2 import InterfaceError, OperationalError
from sqlalchemy.orm import Session

from src.cli.cliente_cli import processar_menu_cliente
from src.cli.gerenciamento_cli import processar_menu_gerenciamento
from src.cli.produto_cli import processar_menu_produto
from src.cli.usuario_cli import (
    garantir_admin_padrao,
    processar_menu_perfil,
    realizar_login,
)
from src.cli.venda_cli import processar_menu_venda
from src.controllers.estoque_controller import EstoqueController
from src.controllers.produto_controller import ProdutoController
from src.controllers.venda_controller import VendaController
from src.database.conexao import Conexao
from src.enums import PapelEnum
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.movimentacao_repository import MovimentacaoRepository
from src.repositories.produto_repository import ProdutoRepository
from src.repositories.venda_repository import VendaRepository
from src.services.estoque_service import EstoqueService
from src.services.produto_service import ProdutoService
from src.services.venda_service import VendaService

INVALIDO = 'Opção inválida.'
PEDIR_ID = 'ID usuario: '


def exibir_menu(usuario_logado):
    print('\n=== Sistema de Gestão ===')
    print('1 - Perfil')
    print('2 - Cliente')
    print('3 - Produto')
    print('4 - Venda')
    if usuario_logado.papel in {PapelEnum.ADMIN, PapelEnum.GERENTE}:
        print('5 - Menu Gerenciamento')

    print('0 - Sair')
    return input('> ')


def processar_menu_principal(
    usuario_logado,
    produto_controller,
    estoque_controller,
    venda_controller,
):
    opcao = exibir_menu(usuario_logado)
    if opcao == '1':
        processar_menu_perfil(usuario_logado)
    elif opcao == '2':
        processar_menu_cliente(usuario_logado)
    elif opcao == '3':
        processar_menu_produto(produto_controller)
    elif opcao == '4':
        processar_menu_venda(venda_controller, usuario_logado, produto_controller)
    elif opcao == '5':
        if usuario_logado.papel in {PapelEnum.ADMIN, PapelEnum.GERENTE}:
            processar_menu_gerenciamento(
                usuario_logado, estoque_controller, venda_controller
            )
        else:
            print(INVALIDO)
    elif opcao == '0':
        return False
    else:
        print(INVALIDO)

    return True


def main():
    # Montagem das dependências
    try:
        conexao_db = Conexao
        garantir_admin_padrao()
        client_repo = ClienteRepository(Session)

        # produto
        produto_repo = ProdutoRepository(conexao_db)
        produto_serv = ProdutoService(produto_repo)
        produto_controller = ProdutoController(produto_serv)

        # estoque movimentacoes
        movimentacao_repo = MovimentacaoRepository(conexao_db)
        estoque_serv = EstoqueService(produto_repo, movimentacao_repo, conexao_db)
        estoque_controller = EstoqueController(estoque_serv)

        # venda
        venda_repo = VendaRepository(conexao_db)
        venda_serv = VendaService(
            conexao_db, venda_repo, produto_repo, client_repo, estoque_serv
        )
        venda_controller = VendaController(venda_serv)

        usuario_logado = realizar_login()

        while processar_menu_principal(
            usuario_logado,
            produto_controller,
            estoque_controller,
            venda_controller,
        ):
            continue

    except OperationalError, InterfaceError:
        print(
            '\nA comunicacaoo com o banco foi interrompida. '
            'O sistema sera encerrado. '
            'Confira a ultima operacao antes de tentar novamente.'
        )
    except KeyboardInterrupt:
        print('\nSistema encerrado pelo usuario.')


if __name__ == '__main__':
    main()
