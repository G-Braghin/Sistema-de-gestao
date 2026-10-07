import csv


def exportar_produtos_vendidos(produtos, caminho):
    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")

        escritor.writerow([
            "ID do produto",
            "Nome",
            "Quantidade vendida",
            "Valor total",
        ])

        for produto in produtos:
            escritor.writerow([
                produto.id_produto,
                produto.nome_produto,
                produto.quantidade_vendida,
                f"{produto.valor_total:.2f}".replace(".", ","),
            ])