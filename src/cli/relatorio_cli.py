from src.cli.filtros_cli import processar_invervalo_personalizado

PRESSIONE_ENTER = "\nPressione [ENTER] para voltar..."


def processar_menu_relatorio(venda_controller, usuario_logado):
    while True:
        opcao = menu_relatorio()
        if opcao == "1":
            resumo_relatorio(venda_controller, usuario_logado)
        elif opcao == "2":
            relatorio_produto(venda_controller, usuario_logado)
        elif opcao == "3":
            print("Relatorio ainda nao disponivel")
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


def relatorio_produto(venda_controller, usuario_logado):
    try:
        intervalo = processar_invervalo_personalizado()

        if intervalo is None:
            return

        data_inicial, data_final = intervalo
        produtos = venda_controller.relatorio_produtos(
            usuario_logado, data_inicial, data_final
        )
        exibir_relatorio_produtos(produtos, data_inicial, data_final)
        input(PRESSIONE_ENTER)
    except (ValueError, PermissionError) as e:
        print(f"\n{e}")
        input(PRESSIONE_ENTER)

# Menu e exibixoes
def menu_relatorio():
    print("\n === Menu Relatorios ===")
    print("1 - Relatorio de Vendas (Resumo)")
    print("2 - Relatorio de Vendas Produtos")
    print("3 - Relatorio de Estoque(Em Breve)")
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


def exibir_relatorio_produtos(produtos, inicio, final):
    if not produtos:
        print("Nenhum produto encontrado.")
        return

    quantidade_total = 0
    valor_total_periodo = 0
    print("-" * 90)
    print(
        f"| PRODUTOS MAIS VENDIDOS | Periodo: {inicio.strftime("%d/%m/%Y")} até {final.strftime("%d/%m/%Y")} | Produtos encontrados:{len(produtos)}"
    )
    print("-" * 90)
    print(
        f"{'ID Prod.':<12}{'Nome Produto':<40}{'Unid. Vendidas':<20}{'Valor Vendido':<10}\n"
    )

    for produto in produtos:
        total_formatado = (
            f"R$ {produto.valor_total:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
        quantidade_total += produto.quantidade_vendida
        valor_total_periodo += produto.valor_total
        print(
            f"{produto.id_produto:<12}{produto.nome_produto:<40}{produto.quantidade_vendida:<20}{total_formatado:<10}"
        )
    valor_total_formatado = (
        f"R$ {valor_total_periodo:,.2f}".replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
    print("-" * 90)
    print(
        f"\n| Total de unidades vendidas no periodo: {quantidade_total} | Valor total vendido no periodo: {valor_total_formatado}|"
    )
