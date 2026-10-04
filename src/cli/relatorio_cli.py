from src.cli.filtros_cli import processar_invervalo_personalizado

PRESSIONE_ENTER = "\nPressione [ENTER] para voltar..."

def processar_menu_relatorio(venda_controller, usuario_logado):
    while True:
        opcao = menu_relatorio()
        if opcao == "1":
            resumo_relatorio(venda_controller, usuario_logado)
        elif opcao == "2":
            "relatorio de vendas produtos"
        elif opcao == "3":
            "relatorio de estoque"
        elif opcao == "0":
            return
        else:
            print("Opcao inválida.")



def resumo_relatorio(venda_controller, usuario_logado):
    try:
        intervalo = processar_invervalo_personalizado()
        
        if intervalo is None:
            return
        
        data_inicial, data_final = intervalo
        relatorio = venda_controller.resumo_relatorio(
            usuario_logado, data_inicial, data_final
        )
        exibir_resumo_relatorio(relatorio)
        input(PRESSIONE_ENTER)
    except (ValueError, PermissionError) as e:
        print(f"\n{e}")
        input(PRESSIONE_ENTER)


 #Menu e exibixoes 
def menu_relatorio():
    print("\n === Menu Relatorios ===")
    print("1 - Relatorio de Vendas (Resumo)")
    print("2 - Relatorio de Vendas Produtos")
    print("3 - Relatorio de Estoque")
    print("0 - Voltar")
    return input("> ")


def exibir_resumo_relatorio(relatorio):
    if not relatorio:
        print("Nenhuma venda encontrada.")
        return

    total_formatado = (
        f"R$ {relatorio.total_periodo:,.2f}".replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
    ticket_formatado = (
        f"R$ {relatorio.ticket_medio:,.2f}".replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
    periodo = f"{relatorio.data_inicial.strftime("%d/%m/%Y")} até {relatorio.data_final.strftime("%d/%m/%Y")}"

    print("-" * 68)
    print(f"|  RESUMO RELATORIO  | Periodo: {periodo:<35}|")
    print("-" * 68)
    print(
        f"| TOTAL: {total_formatado:<16}| Num. Vendas:{relatorio.vendas_concluidas:<6}| Ticket M. {ticket_formatado}  |"
    )
    print("-" * 68)