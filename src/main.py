from src.cli.cliente_cli import processar_menu_cliente
from src.cli.usuario_cli import (
    processar_menu_gerenciamento,
    processar_menu_perfil,
    realizar_login,
)
from src.controllers.cliente_controller import ClienteController
from src.controllers.usuario_controller import UsuarioController
from src.database.conexao import Conexao
from src.entities.enums.papel_usuario import PapelUsuario
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.usuario_repository import UsuarioRepository
from src.services.autenticacao_service import AutenticacaoService
from src.services.cliente_service import ClienteService
from src.services.usuario_service import UsuarioService

INVALIDO = "Opção inválida."
PEDIR_ID = "ID usuario: "


def exibir_menu(usuario_logado):
    print("\n=== Sistema de Gestão ===")
    print("1 - Perfil")
    print("2 - Cliente")
    if usuario_logado.papel in (PapelUsuario.ADMINISTRADOR, PapelUsuario.GERENTE):
        print("3 - Menu Gerenciamento")

    print("0 - Sair")
    return input("> ")


def processar_menu_principal(usuario_controller, usuario_logado, cliente_controller):
    opcao = exibir_menu(usuario_logado)
    if opcao == "1":
        processar_menu_perfil(usuario_controller, usuario_logado)
    elif opcao == "2":
        processar_menu_cliente(usuario_logado, cliente_controller) 
    elif opcao == "3":
        if usuario_logado.papel in (PapelUsuario.ADMINISTRADOR, PapelUsuario.GERENTE):
            processar_menu_gerenciamento(usuario_controller, usuario_logado)
        else:
            print(INVALIDO)
    elif opcao == "0":
        return False
    else:
        print(INVALIDO)

    return True


def main():
    # Montagem das dependências
    conexao_db = Conexao()
    usuario_repo = UsuarioRepository(conexao_db)
    autenticacao_serv = AutenticacaoService(usuario_repo)
    usuario_serv = UsuarioService(usuario_repo, autenticacao_serv)
    usuario_controller = UsuarioController(usuario_serv, autenticacao_serv)

    usuario_controller.garantir_admin_padrao()

    cliente_repo= ClienteRepository(conexao_db)
    cliente_serv= ClienteService(cliente_repo)
    cliente_controller = ClienteController(cliente_serv)

    usuario_logado = realizar_login(usuario_controller)
    while processar_menu_principal(usuario_controller, usuario_logado, cliente_controller):
        continue


if __name__ == "__main__":
    main()
