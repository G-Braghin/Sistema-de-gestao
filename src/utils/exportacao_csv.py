import csv


def exportar_resumo_vendas(relatorio, caminho):
    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(
            [
                "Data inicial",
                "Data final",
                "Vendas concluidas",
                "Valor total",
                "Ticket medio",
            ]
        )
        escritor.writerow(
            [
                relatorio.data_inicial.strftime("%d/%m/%Y"),
                relatorio.data_final.strftime("%d/%m/%Y"),
                relatorio.vendas_concluidas,
                f"{relatorio.total_periodo:.2f}".replace(".", ","),
                f"{relatorio.ticket_medio:.2f}".replace(".", ","),
            ]
        )


def exportar_produtos_vendidos(produtos, caminho):
    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")

        escritor.writerow(
            [
                "ID do produto",
                "Nome",
                "Quantidade vendida",
                "Valor total",
            ]
        )

        for produto in produtos:
            escritor.writerow(
                [
                    produto.id_produto,
                    produto.nome_produto,
                    produto.quantidade_vendida,
                    f"{produto.valor_total:.2f}".replace(".", ","),
                ]
            )


def exportar_relatorio_estoque(produtos, caminho):
    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")

        escritor.writerow(
            [
                "ID do produto",
                "Nome",
                "Marca",
                "Quantidade em estoque",
            ]
        )

        for produto in produtos:
            escritor.writerow(
                [
                    produto.id_produto,
                    produto.nome,
                    produto.marca,
                    produto.quantidade_estoque,
                ]
            )
