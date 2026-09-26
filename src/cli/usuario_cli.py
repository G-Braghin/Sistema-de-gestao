from src.entities.enums.papel_usuario import PapelUsuario

INVALIDO = "Opção inválida."
PEDIR_ID = "ID usuario: "
PRESSIONE_ENTER = "\nPressione [ENTER] para voltar..."
VOLTAR = "0 - Voltar"


def garantir_admin_padrao(usuario_controller):
    usuario = usuario_controller.garantir_admin_padrao()
    if usuario is None:
        return

    print(f"Administrador padrão criado! ID de acesso: {usuario.id_usuario}")
    input(PRESSIONE_ENTER)


def realizar_login(usuario_controller):
    usuario_logado = None
    while usuario_logado == None:
        try:
            id_usuario = int(input("ID: "))
            senha = input("Senha: ")
            usuario_logado = usuario_controller.fazer_login(id_usuario, senha)
            print(f"\nUsuario autenticado: {usuario_logado.nome}")
            input(PRESSIONE_ENTER)
        except (ValueError, TypeError) as e:
            print(f"{e}")
            input(PRESSIONE_ENTER)
    return usuario_logado


def menu_perfil(usuario_logado):
    print("\n=== Menu perfil ===")
    print(f"Nome: {usuario_logado.nome}")
    print(f"ID: {usuario_logado.id_usuario}")
    print(f"Cargo: {usuario_logado.papel.value}")
    print("1 - Trocar senha")
    print(VOLTAR)
    return input("> ")


def processar_menu_perfil(usuario_controller, usuario_logado):
    while True:
        opcao = menu_perfil(usuario_logado)
        if opcao == "1":
            trocar_senha(usuario_controller, usuario_logado)
        elif opcao == "0":
            return
        else:
            print(INVALIDO)


def trocar_senha(usuario_controller, usuario_logado):
    senha_atual = input("Senha atual: ")
    nova_senha = input("Nova senha: ")
    try:
        usuario_controller.atualizar_senha_usuario(
            usuario_logado, senha_atual, nova_senha
        )
        print("Senha atualizada com sucesso.")
        input(PRESSIONE_ENTER)
    except (ValueError, TypeError) as e:
        print(f"{e}")
        input(PRESSIONE_ENTER)


def menu_gerenciamento(usuario_logado):
    print("\n=== Menu Gerenciamento ===")
    print("1 - Criar usuario")
    print("2 - Resetar Senha de usuario")
    print("3 - Desativar usuario")
    if usuario_logado.papel == PapelUsuario.ADMINISTRADOR:
        print("4 - Promover a gerente")

    print(VOLTAR)
    return input("> ")


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


def cadastrar_usuario(usuario_controller, usuario_logado):
    try:
        opcoes = opcoes_cadastro(usuario_controller, usuario_logado)
        print("\nEscolha o cargo:")
        for numero, descricao in opcoes:
            print(f"{numero} - {descricao}")

        opcao = input("> ")
        papel = papel_da_opcao_cadastro(usuario_controller, usuario_logado, opcao)
        if papel is None:
            print(INVALIDO)
            return

        nome = input("Nome: ")
        senha = input("Senha: ")
        usuario_novo = usuario_controller.cadastrar_usuario(
            usuario_logado, nome, senha, papel
        )
        print(
            f"funcionario cadastrado com sucesso! ID de acesso: {usuario_novo.id_usuario}"
        )
    except (PermissionError, ValueError) as e:
        print(f"\n{e}")
        input(PRESSIONE_ENTER)


def opcoes_cadastro(usuario_controller, usuario_logado):
    papeis = usuario_controller.obter_papeis_cadastro(usuario_logado)
    return [(i, papel.value) for i, papel in enumerate(papeis, start=1)]


def papel_da_opcao_cadastro(usuario_controller, usuario_logado, opcao):
    papeis = usuario_controller.obter_papeis_cadastro(usuario_logado)
    try:
        numero = int(opcao)
        if not 1 <= numero <= len(papeis):
            return None
        return papeis[numero - 1]
    except (ValueError, IndexError):
        return None


def resetar_senha_alvo(usuario_controller, usuario_logado):
    try:
        id_usuario = int(input(PEDIR_ID))
        nova_senha = input("Nova senha: ")
        usuario_alvo = usuario_controller.resetar_senha(
            usuario_logado, id_usuario, nova_senha
        )
        print(f"Nova senha para {usuario_alvo.nome} foi feito com Sucesso!")
        input(PRESSIONE_ENTER)
    except (ValueError, TypeError, PermissionError) as e:
        print(f"\n{e}")
        input(PRESSIONE_ENTER)


def desligar_usuario(usuario_controller, usuario_logado):
    try:
        id_usuario = int(input(PEDIR_ID))
        usuario_alvo = usuario_controller.desativar_usuario(usuario_logado, id_usuario)
        print(f"Conta do usuario {usuario_alvo.nome} desativada com Sucesso!")
        input(PRESSIONE_ENTER)
    except (ValueError, TypeError, PermissionError) as e:
        print(f"\n{e}")
        input(PRESSIONE_ENTER)


def promover(usuario_controller, usuario_logado):
    try:
        id_usuario = int(input(PEDIR_ID))
        usuario_promovido = usuario_controller.promover_gerente(
            usuario_logado, id_usuario
        )
        print(f"{usuario_promovido.nome} promovido a Gerente!")
        input(PRESSIONE_ENTER)
    except (ValueError, TypeError, PermissionError) as e:
        print(f"\n{e}")
        input(PRESSIONE_ENTER)


