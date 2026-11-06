from src.cli.filtros_cli import processar_filtro, processar_invervalo_personalizado
from src.cli.produto_cli import listar_produto
from src.database.database import get_session
from src.dependencies.venda_dependencies import get_venda_controller
from src.entities.dtos.venda_resumo import VendaResumo
from src.enums import StatusVenda
from src.models import Venda
from src.utils.filtro_datas import FiltroDatas
from src.utils.fuso import FUSO_HORARIO

VOLTAR = '0 - Voltar'
INVALIDO = 'Opção inválida.'
PRESSIONE_ENTER = '\nPressione [ENTER] para voltar...'
FORMATO_DATA_HORA = '%d/%m/%Y %H:%M'


# Fluxos principais
def processar_menu_venda(usuario_logado):
    while True:
        opcao = menu_venda()
        match opcao:
            case '1':
                realizar_venda(usuario_logado)
            case '0':
                return
            case _:
                print(INVALIDO)


def processar_menu_venda_gerenciamento(usuario_logado):
    while True:
        opcao = menu_venda_gerenciamento()
        match opcao:
            case '1':
                processar_menu_listar_vendas(usuario_logado)
            case '2':
                cancelar_venda(usuario_logado)
            case '0':
                return
            case _:
                print(INVALIDO)


def processar_menu_listar_vendas(usuario_logado):
    while True:
        opcao = menu_listar_vendas()
        match opcao:
            case '1':
                listar_resumo_venda(usuario_logado)
            case '2':
                listar_venda(usuario_logado)
            case '0':
                return
            case _:
                print(INVALIDO)


# Operacoes de venda
def coletar_dados_venda():
    id_cliente = int(input('Inserir ID do cliente: '))
    num_produtos = int(input('Quantidade de itens diferentes a adicionar: '))
    itens = []
    for num in range(1, num_produtos + 1):
        id_produto = int(input(f'ID do {num}º produto: '))
        quantidade = int(input(f'Quantidade do {num}º produto: '))
        itens.append({'id_produto': id_produto, 'quantidade': quantidade})

    return id_cliente, itens


def realizar_venda(usuario_logado):
    print('\n=== Venda ===')
    ver_produto = (
        input('Deseja vizualizar a lista de produtos antes? (S/N)').strip().upper()
    )

    if ver_produto == 'S':
        listar_produto()

    print('======================\n')

    with get_session() as session:
        venda_controller = get_venda_controller(session)
        try:
            id_cliente, itens = coletar_dados_venda()
            venda_controller.realizar_venda(usuario_logado, id_cliente, itens)
            print('Venda realizada com sucesso.')
            input(PRESSIONE_ENTER)
        except (ValueError, TypeError, PermissionError) as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)


def cancelar_venda(usuario_logado):
    with get_session() as session:
        venda_controller = get_venda_controller(session)
        try:
            id_venda = int(input('Insira o ID da venda: '))
            venda_controller.realizar_cancelamento(usuario_logado, id_venda)
            print(f'Venda com ID: {id_venda} cancelada com sucesso.')
            input(PRESSIONE_ENTER)
        except (ValueError, TypeError, PermissionError) as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)


def listar_resumo_venda(usuario_logado):
    status_venda = processar_escolha_status_venda()
    print('\n=== Visualizar Venda ===')
    filtro_data = processar_filtro()

    if filtro_data == '0':
        return

    inicio_filtro = None
    final_filtro = None

    if filtro_data == FiltroDatas.PERSONALIZADO:
        intervalo = processar_invervalo_personalizado()
        if intervalo is None:
            return
        inicio_filtro, final_filtro = intervalo

    with get_session() as session:
        venda_controller = get_venda_controller(session)
        try:
            vendas = venda_controller.listar_resumo(
                usuario_logado, status_venda, filtro_data, inicio_filtro, final_filtro
            )
            exibir_tabela_resumo(vendas)
            input(PRESSIONE_ENTER)
        except (ValueError, TypeError, PermissionError) as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)


def listar_venda(usuario_logado):
    with get_session() as session:
        venda_controller = get_venda_controller(session)
        try:
            id_venda = int(input('Insira o ID da venda: '))
            venda = venda_controller.listar_venda(usuario_logado, id_venda)
            exibir_tabela_venda(venda)
            input(PRESSIONE_ENTER)
        except (ValueError, TypeError, PermissionError) as e:
            print(f'\n{e}')
            input(PRESSIONE_ENTER)


# Processamento das escolhas
def processar_escolha_status_venda():
    while True:
        opcao = escolher_status_venda()
        match opcao:
            case '1':
                return StatusVenda.CONCLUIDA
            case '2':
                return StatusVenda.CANCELADA
            case '3':
                return None
            case _:
                print(INVALIDO)


# Menus e exibicao
def menu_venda():
    print('\n=== Menu Venda ===')
    print('1 - Realizar Venda')
    print(VOLTAR)
    return input('> ')


def menu_venda_gerenciamento():
    print('\n=== Gerenciamento de Venda ===')
    print('1 - Visualizar Vendas')
    print('2 - Cancelar Venda')
    print(VOLTAR)
    return input('> ')


def menu_listar_vendas():
    print('\n=== Menu Visualizar Vendas ===')
    print('1 - Visualizar Resumo Vendas')
    print('2 - Visualizar Venda(ID)')
    print(VOLTAR)
    return input('> ')


def escolher_status_venda():
    print('\n=== Escolher Status da Venda ===')
    print('1 - Concluido')
    print('2 - Cancelado')
    print('3 - Todos')
    return input('> ')


def exibir_tabela_resumo(vendas: list[VendaResumo]):
    if not vendas:
        print('\nNenhuma venda encontrada.')
        return

    print(
        f'\n{"ID Venda":<10}{"Cliente":<20}{"Vendedor":<20}'
        f'{"Data Venda":<20}{"Valor Total":<15}{"Status":<15}'
    )
    print('-' * 100)
    for venda in vendas:
        data_formatada = venda.data_venda.astimezone(FUSO_HORARIO).strftime(
            FORMATO_DATA_HORA
        )
        valor_formatado = f'R$ {venda.valor_total:.2f}'.replace('.', ',')
        print(
            f'{venda.id_venda:<10}{venda.nome_cliente:<20}{venda.nome_vendedor:<20}'
            f'{data_formatada:<20}{valor_formatado:<15}{venda.status.value:<15}'
        )


def exibir_tabela_venda(venda: Venda):
    if not venda:
        print('\nNenhuma venda encontrada.')
        return

    print(
        f'\n{"ID Venda":<10}{"ID Cli.":<10}{"ID User":<10}'
        f'{"Data Venda":<25}{"Valor Total":<15}{"Status":<15}'
    )
    print('-' * 80)
    data_formatada = venda.created_at.astimezone(FUSO_HORARIO).strftime(
        FORMATO_DATA_HORA
    )
    valor_formatado = f'R$ {venda.valor_total:.2f}'.replace('.', ',')
    print(
        f'{venda.id:<10}{venda.id_cliente:<10}{venda.id_usuario:<10}'
        f'{data_formatada:<25}{valor_formatado:<15}{venda.status.value:<15}'
    )

    # if venda.status == StatusVenda.CANCELADA:
    #    data_cancelamento_formatada = (
    #        venda.data_cancelamento.strftime(FORMATO_DATA_HORA)
    #        if venda.data_cancelamento
    #        else 'N/A'
    #    )
    #    print(f'\nVenda cancelada em: {data_cancelamento_formatada}')
    #    print(f'Cancelada por ID de usuário: {venda.id_usuario_cancelamento}')

    print('\nItens da Venda:')
    print(
        f'\n{"ID Produto":<12}{"Nome Produto":<25}{"Quant.":<10}'
        f'{"Preço Unitário":>15}{"Subtotal":>15}'
    )
    print('-' * 80)
    for item in venda.itens:
        preco_unitario_formatado = f'R$ {item.preco_unitario:.2f}'.replace('.', ',')
        sub_total_formatado = f'R$ {item.subtotal:.2f}'.replace('.', ',')
        print(
            f'{item.id_produto:<12}{item.quantidade:<10}'
            f'{preco_unitario_formatado:>15}{sub_total_formatado:>15}'
        )
