from src.database.database import get_session
from src.dependencies.clientes_dependencies import client_controller
from src.enums import PapelEnum

INVALIDO = '\nOpção inválida.'
CPF_CLIENTE = 'CPF do cliente: '
VOLTAR = '0 - Voltar'
PRESSIONE_ENTER = '\nPressione [ENTER] para voltar...'
DIGITE_ZERO_CANCELAR = 'Digite 0 a qualquer momento para cancelar.'


def menu_cliente(usuario_logado):
    print('\n=== Menu Cliente ===')
    print('1 - Cadastrar cliente')
    print('2 - Atualizar informacao cliente')  # fazer outra funcao
    print('3 - Listar clientes ativos')
    if usuario_logado.papel != PapelEnum.FUNCIONARIO:
        print('4 - Listar clientes desativados')
    print(VOLTAR)
    return input('> ')


def menu_atualizar(usuario_logado):
    print('\n=== Atualizar Cliente ===')
    print('1 - Atualizar nome')
    print('2 - Atualizar telefone')
    print('3 - Atualizar endereco')
    if usuario_logado.papel != PapelEnum.FUNCIONARIO:
        print('4 - Atualizar status')
    print(VOLTAR)
    return input('> ')


def cadastrar_cliente():
    print('\n==== Cadastro de Cliente ====')

    nome = input('Nome do Cliente: ')
    cpf = input('CPF: ')
    telefone = input('Telefone: ')
    endereco = input('Endereco: ')

    with get_session() as session:
        cliente_controller = client_controller(session)

        try:
            cliente_novo = cliente_controller.cadastrar_cliente(
                nome, cpf, telefone, endereco
            )
            print('\nCliente cadastrado com sucesso!')
            input(PRESSIONE_ENTER)
            return cliente_novo
        except ValueError as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)
            return None


def atualizar_nome():
    print('\n=== Atualizar nome ===')
    print(DIGITE_ZERO_CANCELAR)

    cpf_cliente = input(CPF_CLIENTE)
    if cpf_cliente.strip() == '0':
        return

    novo_nome = input('Novo nome cliente: ')
    if novo_nome.strip() == '0':
        return

    with get_session() as session:
        cliente_controller = client_controller(session)

        try:
            cliente = cliente_controller.atualizar_nome(cpf_cliente, novo_nome)
            print('\nNovo nome atualizado com Sucesso')
            input(PRESSIONE_ENTER)
            return cliente
        except ValueError as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)
            return None


def atualizar_endereco():
    print('\n=== Atualizar ndereco ===')
    print(DIGITE_ZERO_CANCELAR)

    cpf_cliente = input(CPF_CLIENTE)
    if cpf_cliente.strip() == '0':
        return

    print('Deixe em branco e prescione Enter para apagar o endereco atual.')
    endereco_novo = input('Novo endereco : ')
    if endereco_novo.strip() == '0':
        return

    with get_session() as session:
        cliente_controller = client_controller(session)

        try:
            cliente = cliente_controller.atualizar_endereco(cpf_cliente, endereco_novo)
            print(f'\nEndereco do cliente {cliente.nome} atualizado com sucesso!')
            input(PRESSIONE_ENTER)
            return cliente
        except ValueError as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)
            return None


def atualizar_telefone():
    print('\n=== Atualizar telefone ===')
    print(DIGITE_ZERO_CANCELAR)
    cpf_cliente = input(CPF_CLIENTE)
    if cpf_cliente.strip() == '0':
        return

    telefone_novo = input('Novo telefone: ')
    if telefone_novo.strip() == '0':
        return

    with get_session() as session:
        cliente_controller = client_controller(session)

        try:
            cliente = cliente_controller.atualizar_telefone(cpf_cliente, telefone_novo)
            print(f'\nTelefone do cliente {cliente.nome} atualizado com sucesso!')
            input(PRESSIONE_ENTER)
            return cliente
        except ValueError as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)
            return None


def atualizar_status(usuario_logado):
    opcao = processar_status_opcao()
    if opcao is not None:
        with get_session() as session:
            cliente_controller = client_controller(session)
            try:
                id_cliente = int(input('ID do cliente: '))
                cliente = cliente_controller.atualizar_status(
                    usuario_logado, id_cliente, opcao
                )
                print(f'\nCliente {"ativado" if opcao else "desativado"} com sucesso')
                input(PRESSIONE_ENTER)
                return cliente
            except (ValueError, PermissionError, TypeError) as e:
                print(f'\n{e}')
                input(PRESSIONE_ENTER)
                return None


def listar(usuario_logado, status_ativo: bool = True):
    with get_session() as session:
        cliente_controller = client_controller(session)

        try:
            clientes = cliente_controller.listar_clientes(usuario_logado, status_ativo)
        except PermissionError as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)
            return
        if not clientes:
            print(
                f'\nNenhum cliente {
                    "ativo" if status_ativo else "desativado"
                } encontrado'
            )
            input(PRESSIONE_ENTER)
            return

        exibir_tabela(clientes)


def exibir_tabela(clientes: list):
    print(f'\n{"ID":<5}{"Nome":<25}{"CPF":<20}{"Telefone":<15}{"Endereco":<25}')
    print('-' * 91)
    for cliente in clientes:
        print(
            f'{cliente.id:<5}{cliente.nome:<25}{cliente.cpf:<20}'
            f'{cliente.telefone:<15}{cliente.endereco or "":<25}'
        )
    input(PRESSIONE_ENTER)


def atualizar(usuario_logado):
    while True:
        opcao = menu_atualizar(usuario_logado)
        if opcao == '1':
            atualizar_nome()
        elif opcao == '2':
            atualizar_telefone()
        elif opcao == '3':
            atualizar_endereco()
        elif opcao == '4':
            if usuario_logado.papel != PapelEnum.FUNCIONARIO:
                atualizar_status(usuario_logado)
            else:
                print(INVALIDO)
        elif opcao == '0':
            return
        else:
            print(INVALIDO)


def processar_status_opcao():
    while True:
        print('\n=== Atualizar status ===')
        print('1 - Desativar cliente')
        print('2 - Ativar cliente')
        print(VOLTAR)
        opcao = input('> ')
        if opcao == '1':
            return False
        elif opcao == '2':
            return True
        elif opcao == '0':
            return None
        else:
            print(INVALIDO)


def processar_menu_cliente(usuario_logado):
    while True:
        opcao = menu_cliente(usuario_logado)
        if opcao == '1':
            cadastrar_cliente()
        elif opcao == '2':
            atualizar(usuario_logado)
        elif opcao == '3':
            listar(usuario_logado)
        elif opcao == '4':
            if usuario_logado.papel != PapelEnum.FUNCIONARIO:
                listar(usuario_logado, False)
            else:
                print(INVALIDO)
        elif opcao == '0':
            return
        else:
            print(INVALIDO)
