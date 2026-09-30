from src.entities.enums.motivo_movimentacao import MotivoMovimentacao

INVALIDO = "\nOpção inválida."
PRESSIONE_ENTER = "\nPressione [ENTER] para voltar..."
INSIRA_ID = "Insira o ID do produto: "


# Fluxo principal
def processar_menu_estoque_gerenciamento(estoque_controller, usuario_logado):
    while True:
        opcao = menu_estoque_gerenciamento()
        if opcao == "1":
            registrar_reabastecimento(estoque_controller, usuario_logado)
        elif opcao == "2":
            processar_ajustar_estoque(estoque_controller, usuario_logado)
        elif opcao == "3":
            listar_movimentacoes(estoque_controller, usuario_logado)
        elif opcao == "0":
            return
        else:
            print(INVALIDO)


# Operacoes do estoque
def registrar_reabastecimento(estoque_controller, usuario_logado):
    print("\nRegistrar Reabastecimento")
    try:
        id_produto = int(input(INSIRA_ID))
        entrada_estoque = int(input("Insira a quantidade e ser reabastecida: "))
        produto = estoque_controller.dar_entrada(
            usuario_logado, id_produto, entrada_estoque, MotivoMovimentacao.REPOSICAO
        )
        print(
            f"Entrada de {entrada_estoque} item(s) registrada com sucesso em {produto.nome}"
        )
        input(PRESSIONE_ENTER)
    except (ValueError, TypeError, PermissionError) as e:
        print(f"\n{e}")
        input(PRESSIONE_ENTER)


def processar_ajustar_estoque(estoque_controller, usuario_logado):
    while True:
        opcao = menu_ajustar_estoque()
        if opcao == "1":
            ajustar_mais(estoque_controller, usuario_logado)
        elif opcao == "2":
            ajustar_menos(estoque_controller, usuario_logado)
        elif opcao == "0":
            return
        else:
            print(INVALIDO)


def ajustar_mais(estoque_controller, usuario_logado):
    print("\nAJUSTE -- Adicionar...")
    try:
        id_produto = int(input(INSIRA_ID))
        entrada_estoque = int(input("Insira a quantidade a ser adicionada no ajuste: "))
        produto = estoque_controller.dar_entrada(
            usuario_logado, id_produto, entrada_estoque, MotivoMovimentacao.AJUSTE
        )
        print(f"ajuste em {produto.nome} realizado com sucesso. ")
        input(PRESSIONE_ENTER)
    except (ValueError, TypeError, PermissionError) as e:
        print(f"\n{e}")
        input(PRESSIONE_ENTER)


def ajustar_menos(estoque_controller, usuario_logado):
    print("\nAJUSTE -- Remover...")
    try:
        id_produto = int(input(INSIRA_ID))
        saida_estoque = int(input("Insira a quantidade a ser removida no ajuste: "))
        produto = estoque_controller.dar_saida(
            usuario_logado, id_produto, saida_estoque, MotivoMovimentacao.AJUSTE
        )
        print(f"ajuste em {produto.nome} realizado com sucesso. ")
        input(PRESSIONE_ENTER)
    except (ValueError, TypeError, PermissionError) as e:
        print(f"\n{e}")
        input(PRESSIONE_ENTER)


def listar_movimentacoes(estoque_controller, usuario_logado):
    try:
        movimentacoes = estoque_controller.listar_movimentacoes(usuario_logado)
    except PermissionError as e:
        print(f"\n{e}")
        input(PRESSIONE_ENTER)

    if not movimentacoes:
        print("\nNenhuma movimentacao encontrada.")
        return

    exibir_tabela(movimentacoes)


# Menus e apresentacao
def menu_estoque_gerenciamento():
    print("\n=== Menu Estoque Gerenciamento===")
    print("1 - Registrar reabastecimento")
    print("2 - Ajustar estoque(Correcoes/Sobra/Perda)")
    print("3 - Listar movimentacoes(Historico)")
    print("0 - Voltar")
    return input("> ")


def menu_ajustar_estoque():
    print("\n=== Ajustar Estoque ===")
    print("1 - Corrigir para MAIS")
    print("2 - Corrigir para MENOS")
    print("0 - Voltar")
    return input("> ")


# Auxiliar de apresentacao
def exibir_tabela(movimentacoes):
    print(
        f"\n{'ID Mov.':<10}{'ID Prod.':<10}{'ID Resp.':<10}{'Entrada/Saida':<15}"
        f"{'Quant':<10}{'Data/Hora':<20}{'Motivo':<15}{'ID Venda':<10}"
    )
    print("-" * 105)
    for movimentacao in movimentacoes:
        data_formatada = movimentacao.data_hora.strftime("%d/%m/%Y %H:%M")
        id_vend = "-" if movimentacao.id_venda is None else movimentacao.id_venda
        print(
            f"{movimentacao.id_movimentacao:<10}{movimentacao.id_produto:<10}"
            f"{movimentacao.id_usuario:<10}{movimentacao.tipo.value:<15}"
            f"{movimentacao.quantidade:<10}{data_formatada:<20}"
            f"{movimentacao.motivo.value:<15}{id_vend:<10}"
        )
    input(PRESSIONE_ENTER)
