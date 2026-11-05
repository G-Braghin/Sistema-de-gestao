from psycopg2 import InterfaceError, OperationalError

from src.cli.cliente_cli import processar_menu_cliente
from src.cli.gerenciamento_cli import processar_menu_gerenciamento
from src.cli.produto_cli import processar_menu_produto
from src.cli.usuario_cli import (
    garantir_admin_padrao,
    processar_menu_perfil,
    realizar_login,
)
from src.cli.venda_cli import processar_menu_venda
from src.enums import PapelEnum

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
):
    opcao = exibir_menu(usuario_logado)
    if opcao == '1':
        processar_menu_perfil(usuario_logado)
    elif opcao == '2':
        processar_menu_cliente(usuario_logado)
    elif opcao == '3':
        processar_menu_produto()
    elif opcao == '4':
        processar_menu_venda(usuario_logado)
    elif opcao == '5':
        if usuario_logado.papel in {PapelEnum.ADMIN, PapelEnum.GERENTE}:
            processar_menu_gerenciamento(usuario_logado)
        else:
            print(INVALIDO)
    elif opcao == '0':
        return False
    else:
        print(INVALIDO)

    return True


def main():
    try:
        garantir_admin_padrao()

        usuario_logado = realizar_login()

        while processar_menu_principal(
            usuario_logado,
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
