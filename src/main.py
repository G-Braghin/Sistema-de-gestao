from src.database.conexao import Conexao
from src.repositories.usuario_repository import UsuarioRepository
from src.services.autenticacao_service import AutenticacaoService
from src.services.usuario_service import UsuarioService
from src.controllers.usuario_controller import UsuarioController
from src.entities.enums.papel_usuario import PapelUsuario

INVALIDO = "Opção inválida."
PEDIR_ID = "ID usuario: "

def pedir_id():
    while True:
        try:
            return int(input(PEDIR_ID))
        except ValueError:
            print ("Id deve ser um numero.")

def realizar_login(usuario_controller):
    usuario_logado = None
    while usuario_logado == None:
        try:
            id_usuario = int(input("ID: "))
            senha = input("Senha: ")
            usuario_logado = usuario_controller.fazer_login(id_usuario, senha)
        except ValueError:
            print("ID deve ser um número.")
    return usuario_logado

def exibir_menu(usuario_logado):
    print("\n=== Sistema de Gestão ===")
    print("1 - Perfil")
    if usuario_logado.papel in (PapelUsuario.ADMINISTRADOR, PapelUsuario.GERENTE):
        print("2 - Menu Gerenciamento")

    print("0 - Sair")
    return input("> ")

def menu_perfil(usuario_logado):
    print("\n=== Menu perfil ===")
    print(f"Nome: {usuario_logado.nome}")
    print(f"ID: {usuario_logado.id_usuario}")
    print(f"Cargo: {usuario_logado.papel.value}")
    print("1 - Trocar senha")
    print("0 - Voltar")
    return input("> ")

def menu_gerenciamento(usuario_logado):
    print("\n=== Menu Gerenciamento ===")
    print("1 - Criar usuario") 
    print("2 - Resetar Senha de usuario")
    print("3 - Desativar usuario")
    if usuario_logado.papel == PapelUsuario.ADMINISTRADOR:
        print("4 - Promover a gerente")

    print("0 - Voltar")
    return input("> ")

def trocar_senha(usuario_controller, usuario_logado):
    senha_atual = input("Senha atual: ")
    nova_senha = input("Nova senha: ")
    usuario_controller.atualizar_senha_usuario(usuario_logado, senha_atual, nova_senha)

def cadastrar_usuario(usuario_controller, usuario_logado):
    opcoes = usuario_controller.opcoes_cadastro(usuario_logado)
    if not opcoes:
        print("Você não tem permissão para cadastrar usuários.")
        return

    print("\nEscolha o cargo:")
    for numero, descricao in opcoes:
        print(f"{numero} - {descricao}")

    opcao = input("> ")
    papel = usuario_controller.papel_da_opcao_cadastro(usuario_logado, opcao)
    if papel is None:
        print(INVALIDO)
        return

    nome = input("Nome: ")
    senha = input("Senha: ")
    usuario_controller.cadastrar_usuario(usuario_logado, nome, senha, papel)

def desligar_usuario(usuario_controller,usuario_logado):
    id_usuario = pedir_id()
    usuario_controller.desativar_usuario(usuario_logado,id_usuario)

def resetar_senha_alvo(usuario_controller,usuario_logado):
    id_usuario = pedir_id()
    nova_senha= input("Nova senha: ")
    usuario_controller.resetar_senha(usuario_logado,id_usuario,nova_senha)
    
def promover(usuario_controller,usuario_logado):
    id_usuario = pedir_id()
    usuario_controller.promover_gerente(usuario_logado,id_usuario)

def processar_menu_perfil(usuario_controller,usuario_logado):
    while True:
        opcao = menu_perfil(usuario_logado)
        if opcao == "1":
            trocar_senha(usuario_controller,usuario_logado)
        elif opcao == "0":
            return
        else:
            print(INVALIDO)

def processar_menu_gerenciamento(usuario_controller, usuario_logado):
    while True:
        opcao = menu_gerenciamento(usuario_logado)
        if opcao == "1":
            cadastrar_usuario(usuario_controller, usuario_logado)
        elif opcao == "2":
            resetar_senha_alvo(usuario_controller, usuario_logado)
        elif opcao == "3":
            desligar_usuario(usuario_controller, usuario_logado)
        elif opcao == "4":
            if usuario_logado.papel == PapelUsuario.ADMINISTRADOR:
                promover(usuario_controller, usuario_logado)
            else:
                print(INVALIDO)
        elif opcao == "0":
            return
        else:
            print(INVALIDO)

def processar_menu_principal(usuario_controller, usuario_logado):
    opcao = exibir_menu(usuario_logado)
    if opcao == "1":
        processar_menu_perfil(usuario_controller, usuario_logado)
    elif opcao == "2":
        if usuario_logado.papel in (PapelUsuario.ADMINISTRADOR,PapelUsuario.GERENTE):
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

    usuario_logado = realizar_login(usuario_controller)
    while processar_menu_principal(usuario_controller, usuario_logado):
        continue

if __name__ == "__main__":
    main()