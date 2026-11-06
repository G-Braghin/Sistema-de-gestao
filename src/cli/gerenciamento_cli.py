from src.cli.estoque_cli import processar_menu_estoque_gerenciamento
from src.cli.relatorio_cli import processar_menu_relatorio
from src.cli.usuario_cli import (
    alterar_status_menu,
    cadastrar_usuario,
    listar_menu,
    promover,
    resetar_senha_alvo,
)
from src.cli.venda_cli import processar_menu_venda_gerenciamento
from src.enums import PapelEnum

INVALIDO = 'Opção inválida.'
VOLTAR = '0 - Voltar'


def menu_gerenciamento(usuario_logado):
    print('\n=== Menu Gerenciamento ===')
    print('1 - Criar usuario')
    print('2 - Resetar Senha de usuario')
    print('3 - Alterar status usuario')
    print('4 - Listar usuarios')
    print('5 - Estoque')
    print('6 - Gerenciamento de Vendas')
    print('7 - Relatorios')
    if usuario_logado.papel == PapelEnum.ADMIN:
        print('8 - Promover a gerente')
    print(VOLTAR)
    return input('> ')


def processar_menu_gerenciamento(usuario_logado):
    while True:
        opcao = menu_gerenciamento(usuario_logado)
        match opcao:
            case '1':
                cadastrar_usuario(usuario_logado)
            case '2':
                resetar_senha_alvo(usuario_logado)
            case '3':
                alterar_status_menu(usuario_logado)
            case '4':
                listar_menu(usuario_logado)
            case '5':
                processar_menu_estoque_gerenciamento(usuario_logado)
            case '6':
                processar_menu_venda_gerenciamento(usuario_logado)
            case '7':
                processar_menu_relatorio(usuario_logado)
            case '8' if usuario_logado.papel == PapelEnum.ADMIN:
                promover(usuario_logado)
            case '0':
                return
            case _:
                print(INVALIDO)
