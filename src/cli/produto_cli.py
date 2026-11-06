from src.database.database import get_session
from src.dependencies.produtos_dependencies import get_produto_controller

VOLTAR = '0 - Voltar'
INVALIDO = '\nOpção inválida.'
PRESSIONE_ENTER = '\nPressione [ENTER] para voltar...'
INFORMAR_ID = 'Informe o ID do produto: '


# Fluxo principal
def processar_menu_produto():
    while True:
        opcao = menu_produto()
        match opcao:
            case '1':
                listar_produto()
            case '2':
                cadastrar_produto()
            case '3':
                processar_menu_atualizar()
            case '0':
                return
            case _:
                print(INVALIDO)


def processar_menu_atualizar():
    while True:
        opcao = menu_atualizar()
        match opcao:
            case '1':
                atualizar_nome()
            case '2':
                atualizar_preco()
            case '0':
                return
            case _:
                print(INVALIDO)


# Operaçoes de produto
def listar_produto():
    with get_session() as session:
        produto_controller = get_produto_controller(session)
        produtos = produto_controller.listar_produtos()
        if not produtos:
            print('Nenhum produto registrado.')
            input(PRESSIONE_ENTER)
            return

        exibir_tabela(produtos)


def cadastrar_produto():
    nome = input('Digite o nome do produto: ')
    preco = input('Digite o preco do produto (Ex: 59,99): ')
    with get_session() as session:
        produto_controller = get_produto_controller(session)
        try:
            preco_formatado = float(preco.replace(',', '.'))
            produto_novo = produto_controller.cadastrar_produto(nome, preco_formatado)
            print(f'{produto_novo.nome} cadastrado com sucesso! ID: {produto_novo.id}')
            input(PRESSIONE_ENTER)
        except ValueError as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)


def atualizar_nome():
    print('\nAtualizar Nome...')
    with get_session() as session:
        produto_controller = get_produto_controller(session)
        try:
            id_produto = int(input(INFORMAR_ID))
            novo_nome = input('Informe o nome do produto: ')
            produto = produto_controller.atualizar_nome(id_produto, novo_nome)
            print(f'Nome atualizado para {produto.nome}')
            input(PRESSIONE_ENTER)
        except (ValueError, TypeError) as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)


# Menus e funçoes auxiliares
def menu_produto():
    print('\n=== Menu Produto ===')
    print('1 - listar produtos')
    print('2 - Cadastrar produto')
    print('3 - Atualizar informacoes')
    print(VOLTAR)
    return input('> ')


def menu_atualizar():
    print('\n=== Atualizar Informacoes Produto ===')
    print('1 - Nome')
    print('2 - Preco')
    print(VOLTAR)
    return input('> ')


def exibir_tabela(produtos: list) -> None:
    print(f'\n{"ID":<5}{"Nome":<20}{"Preco":>10}{"Estoque":>10}')
    print('-' * 65)
    for produto in produtos:
        print(
            f'{produto.id:<5}{produto.nome:<20}{produto.preco:>10}{produto.quantidade:>9}'
        )
    input(PRESSIONE_ENTER)


def atualizar_preco():
    print('\nAtualizar Preco...')
    with get_session() as session:
        produto_controller = get_produto_controller(session)
        try:
            id_produto = int(input(INFORMAR_ID))
            novo_preco = input('Informe o novo preco do produto(Ex: 59,99): ')
            produto = produto_controller.atualizar_preco(id_produto, novo_preco)
            print(f'Preco de {produto.nome} atualizou para $ {produto.preco}')
            input(PRESSIONE_ENTER)
        except (ValueError, TypeError) as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)
