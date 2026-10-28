from src.database.database import get_session
from src.dependencies.usuarios_dependencies import user_controler

INVALIDO = 'Opção inválida.'
PEDIR_ID = 'ID usuario: '
PRESSIONE_ENTER = '\nPressione [ENTER] para voltar...'
VOLTAR = '0 - Voltar'


def garantir_admin_padrao():
    with get_session() as session:
        usuario_controller = user_controler(session)
        usuario = usuario_controller.garantir_admin_padrao()
        if usuario is None:
            return

        print(f'Administrador padrão criado! ID de acesso: {usuario.id}')
        input(PRESSIONE_ENTER)


def realizar_login():
    with get_session() as session:
        usuario_controller = user_controler(session)
        usuario_logado = None
        while usuario_logado is None:
            try:
                id_user = int(input('ID: '))
                senha = input('Senha: ')
                usuario_logado = usuario_controller.fazer_login(id_user, senha)
                print(f'\nUsuario autenticado: {usuario_logado.nome}')
                input(PRESSIONE_ENTER)
            except (ValueError, TypeError) as e:
                print(f'{e}')
                input(PRESSIONE_ENTER)
        return usuario_logado


def menu_perfil(usuario_logado):
    print('\n=== Menu perfil ===')
    print(f'Nome: {usuario_logado.nome}')
    print(f'ID: {usuario_logado.id}')
    print(f'Cargo: {usuario_logado.papel.value}')
    print('1 - Trocar senha')
    print(VOLTAR)
    return input('> ')


def processar_menu_perfil(usuario_logado):
    while True:
        opcao = menu_perfil(usuario_logado)
        if opcao == '1':
            trocar_senha(usuario_logado)
        elif opcao == '0':
            return
        else:
            print(INVALIDO)


def trocar_senha(usuario_logado):
    with get_session() as session:
        usuario_controller = user_controler(session)
        senha_atual = input('Senha atual: ')
        nova_senha = input('Nova senha: ')
        try:
            usuario_controller.atualizar_senha_usuario(
                usuario_logado, senha_atual, nova_senha
            )
            print('Senha atualizada com sucesso.')
            input(PRESSIONE_ENTER)
        except (ValueError, TypeError) as e:
            print(f'{e}')
            input(PRESSIONE_ENTER)


def cadastrar_usuario(usuario_logado):
    with get_session() as session:
        usuario_controller = user_controler(session)
        try:
            opcoes = opcoes_cadastro(usuario_controller, usuario_logado)
            print('\nEscolha o cargo:')
            for numero, descricao in opcoes:
                print(f'{numero} - {descricao}')

            opcao = input('> ')
            papel = papel_da_opcao_cadastro(usuario_controller, usuario_logado, opcao)
            if papel is None:
                print(INVALIDO)
                return

            nome = input('Nome: ')
            senha = input('Senha: ')
            usuario_novo = usuario_controller.cadastrar_usuario(
                usuario_logado, nome, senha, papel
            )
            print(
                f'funcionario cadastrado com sucesso! ID de acesso: {usuario_novo.id}'
            )
        except (PermissionError, ValueError) as e:
            print(f'\n{e}')
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
    except ValueError, IndexError:
        return None


def resetar_senha_alvo(usuario_logado):
    with get_session() as session:
        usuario_controller = user_controler(session)
        try:
            id_user = int(input(PEDIR_ID))
            nova_senha = input('Nova senha: ')
            usuario_alvo = usuario_controller.resetar_senha(
                usuario_logado, id_user, nova_senha
            )
            print(f'Nova senha para {usuario_alvo.nome} foi feito com Sucesso!')
            input(PRESSIONE_ENTER)
        except (ValueError, TypeError, PermissionError) as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)


def alterar_status_menu(usuario_logado):
    while True:
        print('\n===Alterar status ===')
        print('1 - Desativar usuario')
        print('2 - Ativar usuario')
        print(VOLTAR)
        opcao = input('> ')

        if opcao == '1':
            alterar_status_ativo(usuario_logado, False)
        elif opcao == '2':
            alterar_status_ativo(usuario_logado, True)
        elif opcao == '0':
            return
        else:
            print(INVALIDO)


def alterar_status_ativo(usuario_logado, status_ativo):
    with get_session() as session:
        usuario_controller = user_controler(session)
        try:
            id_user = int(input(PEDIR_ID))

            usuario_alvo = usuario_controller.atualizar_status(
                usuario_logado, id_user, status_ativo
            )

            print(
                f'Conta do usuario {usuario_alvo.nome} '
                f'{"ativado" if status_ativo else "desativado"} com sucesso.'
            )
            input(PRESSIONE_ENTER)
        except (ValueError, TypeError, PermissionError) as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)


def listar_menu(usuario_logado):
    while True:
        print('\n=== Listar Usuarios ===')
        print('1 - Usuarios ativos')
        print('2 - Usuarios desativados')
        print(VOLTAR)
        opcao = input('> ')

        if opcao == '1':
            listar(usuario_logado, True)
        elif opcao == '2':
            listar(usuario_logado, False)
        elif opcao == '0':
            return
        else:
            print(INVALIDO)


def listar(usuario_logado, status_ativo):
    with get_session() as session:
        usuario_controller = user_controler(session)
        try:
            usuarios = usuario_controller.listar_usuarios(usuario_logado, status_ativo)
        except PermissionError as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)
            return

        if not usuarios:
            print('Nenhum usuarios encontrado.')
            input(PRESSIONE_ENTER)
            return

        exibir_tabela(usuarios)


def exibir_tabela(usuarios):
    print(f'\n{"ID":<5}{"Nome":<25}{"Cargo":<18}{"Status":<10}')
    print('-' * 58)

    for usuario in usuarios:
        status = 'Ativo' if usuario.ativo else 'Inativo'
        print(f'{usuario.id:<5}{usuario.nome:<25}{usuario.papel.value:<18}{status:<10}')

    input(PRESSIONE_ENTER)


def promover(usuario_logado):
    with get_session() as session:
        usuario_controller = user_controler(session)
        try:
            id_user = int(input(PEDIR_ID))
            usuario_promovido = usuario_controller.promover_gerente(
                usuario_logado, id_user
            )
            print(f'{usuario_promovido.nome} promovido a Gerente!')
            input(PRESSIONE_ENTER)
        except (ValueError, TypeError, PermissionError) as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)
