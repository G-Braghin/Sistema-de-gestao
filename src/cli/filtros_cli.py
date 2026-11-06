from datetime import datetime

from src.utils.filtro_datas import FiltroDatas

INVALIDO = 'Opção inválida.'


def processar_filtro():
    opcoes = {
        '': FiltroDatas.MES_ATUAL,
        '1': FiltroDatas.HOJE,
        '2': FiltroDatas.ONTEM,
        '3': FiltroDatas.ULTIMOS_7_DIAS,
        '4': FiltroDatas.ULTIMOS_30_DIAS,
        '5': FiltroDatas.MES_ATUAL,
        '6': FiltroDatas.MES_ANTERIOR,
        '7': FiltroDatas.ANO_ATUAL,
        '8': FiltroDatas.ANO_ANTERIOR,
        '9': FiltroDatas.PERSONALIZADO,
        '0': '0',
    }
    while True:
        opcao = filtro_data_menu().strip()
        if opcao in opcoes:
            return opcoes[opcao]
        print(INVALIDO)


def processar_invervalo_personalizado():
    while True:
        inicio = input('Digite a data inicial (DD/MM/AAAA ou 0 para voltar): ').strip()
        if inicio == '0':
            return None

        final = input('Digite a data final (DD/MM/AAAA ou 0 para voltar): ').strip()
        if final == '0':
            return None
        try:
            inicio_filtro = datetime.strptime(inicio, '%d/%m/%Y').date()  # noqa: DTZ007
            final_filtro = datetime.strptime(final, '%d/%m/%Y').date()  # noqa: DTZ007
            return inicio_filtro, final_filtro

        except ValueError:
            print('Formato Invalido! Use DD/MM/AAAA.')


def filtro_data_menu():
    print('\n=== Filtros ===')
    print('ENTER - Padrao')
    print('1 - Dia')
    print('2 - Ontem')
    print('3 - 7 dias')
    print('4 - 30 dias')
    print('5 - Neste Mes')
    print('6 - Mes anterior')
    print('7 - Deste ano')
    print('8 - Ano passado')
    print('9 - Personalizado')
    print('0 - Voltar')
    return input('> ')
