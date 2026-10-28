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
from src.entities.enums.papel_usuario import PapelUsuario

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
    if usuario_logado.papel == PapelUsuario.ADMINISTRADOR:
        print('8 - Promover a gerente')
    print(VOLTAR)
    return input('> ')


def processar_menu_gerenciamento(usuario_logado, estoque_controller, venda_controller):
    while True:
        opcao = menu_gerenciamento(usuario_logado)
        if opcao == '1':
            cadastrar_usuario(usuario_logado)
        elif opcao == '2':
            resetar_senha_alvo(usuario_logado)
        elif opcao == '3':
            alterar_status_menu(usuario_logado)
        elif opcao == '4':
            listar_menu(usuario_logado)
        elif opcao == '5':
            processar_menu_estoque_gerenciamento(estoque_controller, usuario_logado)
        elif opcao == '6':
            processar_menu_venda_gerenciamento(venda_controller, usuario_logado)
        elif opcao == '7':
            processar_menu_relatorio(
                venda_controller, usuario_logado, estoque_controller
            )
        elif opcao == '8':
            if usuario_logado.papel == PapelUsuario.ADMINISTRADOR:
                promover(usuario_logado)
            else:
                print(INVALIDO)
        elif opcao == '0':
            return
        else:
            print(INVALIDO)
