from datetime import datetime

from src.utils.filtro_datas import FiltroDatas

INVALIDO = "Opção inválida."

def processar_filtro():
    while True:
        opcao = filtro_data_menu().strip()
        if opcao == "":
            return FiltroDatas.MES_ATUAL
        elif opcao == "1":
            return FiltroDatas.HOJE
        elif opcao == "2":
            return FiltroDatas.ONTEM
        elif opcao == "3":
            return FiltroDatas.ULTIMOS_7_DIAS
        elif opcao == "4":
            return FiltroDatas.ULTIMOS_30_DIAS
        elif opcao == "5":
            return FiltroDatas.MES_ATUAL
        elif opcao == "6":
            return FiltroDatas.MES_ANTERIOR
        elif opcao == "7":
            return FiltroDatas.ANO_ATUAL
        elif opcao == "8":
            return FiltroDatas.ANO_ANTERIOR
        elif opcao == "9":
            return FiltroDatas.PERSONALIZADO
        elif opcao == "0":
            return "0"
        else:
            print(INVALIDO)


def processar_invervalo_personalizado():
    while True:
        inicio = input("Digite a data inicial (DD/MM/AAAA ou 0 para voltar): ").strip()
        if inicio == "0":
            return None

        final = input("Digite a data final (DD/MM/AAAA ou 0 para voltar): ").strip()
        if final == "0":
            return None
        try:
            inicio_filtro = datetime.strptime(inicio, "%d/%m/%Y").date()  # noqa: DTZ007
            final_filtro = datetime.strptime(final, "%d/%m/%Y").date()  # noqa: DTZ007
            return inicio_filtro, final_filtro

        except ValueError:
            print("Formato Invalido! Use DD/MM/AAAA.")




def filtro_data_menu():
    print("\n=== Filtros ===")
    print("ENTER - Padrao")
    print("1 - Dia")
    print("2 - Ontem")
    print("3 - 7 dias")
    print("4 - 30 dias")
    print("5 - Neste Mes")
    print("6 - Mes anterior")
    print("7 - Deste ano")
    print("8 - Ano passado")
    print("9 - Personalizado")
    print("0 - Voltar")
    return input("> ")